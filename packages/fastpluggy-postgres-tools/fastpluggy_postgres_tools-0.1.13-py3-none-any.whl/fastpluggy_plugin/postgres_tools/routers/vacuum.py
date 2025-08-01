from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from fastpluggy.core.database import get_db
from fastpluggy.core.dependency import get_view_builder
from fastpluggy.core.widgets import TableWidget, ButtonWidget
from fastpluggy.core.menu.decorator import menu_entry

vacuum_router = APIRouter(prefix="/vacuum", tags=["postgres_vacuum"])


class VacuumRequest(BaseModel):
    schema_name: Optional[str] = None
    table_name: Optional[str] = None
    analyze: bool = True
    full: bool = False


def get_table_vacuum_status(db: Session, schema: str = None, days_since_vacuum: int = None):
    """
    Get vacuum status for tables
    """
    where_clause = "WHERE schemaname NOT IN ('pg_catalog', 'information_schema')"
    if schema:
        where_clause += f" AND schemaname = '{schema}'"
    if days_since_vacuum:
        where_clause += f" AND EXTRACT(EPOCH FROM (now() - COALESCE(last_vacuum, last_autovacuum, '1970-01-01'::timestamp)))/86400 > {days_since_vacuum}"
        
    query = text(f"""
        SELECT 
          schemaname, 
          relname, 
          last_vacuum, 
          last_autovacuum, 
          n_dead_tup,
          EXTRACT(EPOCH FROM (now() - COALESCE(last_vacuum, last_autovacuum, '1970-01-01'::timestamp)))/86400 AS days_since_vacuum,
          CASE 
            WHEN EXTRACT(EPOCH FROM (now() - COALESCE(last_vacuum, last_autovacuum, '1970-01-01'::timestamp)))/86400 > 30 THEN 'error'
            WHEN EXTRACT(EPOCH FROM (now() - COALESCE(last_vacuum, last_autovacuum, '1970-01-01'::timestamp)))/86400 > 14 THEN 'warning'
            ELSE 'ok'
          END AS status
        FROM pg_stat_user_tables
        {where_clause}
        ORDER BY days_since_vacuum DESC
    """)
    

    result = db.execute(query).mappings()
    return [dict(row) for row in result]


def get_current_vacuum_progress(db: Session):
    """
    Get current vacuum progress
    """
    query = text("""
        SELECT 
          a.pid,
          a.datname,
          a.usename,
          p.relid::regclass AS table_name,
          p.phase,
          p.heap_blks_total,
          p.heap_blks_scanned,
          p.heap_blks_vacuumed,
          ROUND(100.0 * p.heap_blks_scanned / NULLIF(p.heap_blks_total, 0), 2) AS percent_complete
        FROM pg_stat_progress_vacuum p
        JOIN pg_stat_activity a ON p.pid = a.pid
    """)
    

    result = db.execute(query).mappings()
    return [dict(row) for row in result]


def get_autovacuum_settings(db: Session):
    """
    Get autovacuum settings
    """
    query = text("""
        SELECT 
          name, 
          setting, 
          unit, 
          context 
        FROM pg_settings 
        WHERE name LIKE 'autovacuum%'
    """)
    

    result = db.execute(query).mappings()
    return [dict(row) for row in result]


def execute_vacuum(db: Session, vacuum_request: VacuumRequest):
    """
    Execute vacuum operation on specified table(s)
    """
    try:
        # Build the vacuum command
        vacuum_cmd = "VACUUM"
        if vacuum_request.full:
            vacuum_cmd += " FULL"
        if vacuum_request.analyze:
            vacuum_cmd += " ANALYZE"
        
        # Add table specification if provided
        if vacuum_request.table_name:
            if vacuum_request.schema_name:
                table_spec = f'"{vacuum_request.schema_name}"."{vacuum_request.table_name}"'
            else:
                table_spec = f'"{vacuum_request.table_name}"'
            vacuum_cmd += f" {table_spec}"
        
        # Execute the vacuum command
        db.execute(text(vacuum_cmd))
        db.commit()
        
        return {
            "success": True,
            "message": f"Vacuum operation completed successfully",
            "command": vacuum_cmd
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Vacuum operation failed: {str(e)}")


@vacuum_router.post("/execute")
async def trigger_vacuum(
    vacuum_request: VacuumRequest,
    db=Depends(get_db)
):
    """
    Trigger a vacuum operation
    """
    result = execute_vacuum(db, vacuum_request)
    return result


@vacuum_router.get("")
@menu_entry(
    label="Vacuum Status",
    icon="fa fa-broom",
    parent="postgres_tools"
)
async def get_vacuum_view(
    request: Request, 
    db=Depends(get_db), 
    view_builder=Depends(get_view_builder),
    schema: str = None,
    days_since_vacuum: int = None
):
    """
    Get the PostgreSQL vacuum status view
    """
    # Get vacuum status data
    vacuum_status = get_table_vacuum_status(db, schema, days_since_vacuum)
    vacuum_progress = get_current_vacuum_progress(db)
    autovacuum_settings = get_autovacuum_settings(db)
    
    # Create widgets
    vacuum_status_table = TableWidget(
        title="Table Vacuum Status",
        endpoint="/postgres/vacuum",
        data=vacuum_status,
        description="Tables that haven't been vacuumed in over 14 days are highlighted in yellow, over 30 days in red."
    )
    
    # Create a card for vacuum progress if there are any active vacuum processes
    widgets = [vacuum_status_table]
    
    if vacuum_progress:
        progress_table = TableWidget(
            title="Current Vacuum Progress",
            endpoint="/postgres/vacuum",
            data=vacuum_progress
        )
        widgets.append(progress_table)
    
    # Create a table for autovacuum settings
    settings_table = TableWidget(
        title="Autovacuum Settings",
        endpoint="/postgres/vacuum",
        data=autovacuum_settings
    )
    widgets.append(settings_table)
    
    # Add vacuum action buttons
    vacuum_button = ButtonWidget(
        title="Vacuum Operations",
        buttons=[
            {
                "label": "Run VACUUM ANALYZE (All Tables)",
                "endpoint": "/postgres/vacuum/execute",
                "method": "POST",
                "data": {"analyze": True, "full": False},
                "class": "btn-primary",
                "confirm": "Are you sure you want to run VACUUM ANALYZE on all tables? This may take some time."
            },
            {
                "label": "Run VACUUM FULL ANALYZE (All Tables)",
                "endpoint": "/postgres/vacuum/execute", 
                "method": "POST",
                "data": {"analyze": True, "full": True},
                "class": "btn-warning",
                "confirm": "Are you sure you want to run VACUUM FULL ANALYZE on all tables? This will lock tables and may take a long time."
            }
        ]
    )
    widgets.append(vacuum_button)
    
    # Render the view
    return view_builder.generate(
        request,
        title="PostgreSQL Vacuum/Autovacuum Status",
        widgets=widgets
    )