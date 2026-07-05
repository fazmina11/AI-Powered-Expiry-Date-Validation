"""
community/routes/__init__.py
"""
from app.community.routes.user_routes        import router as user_router
from app.community.routes.report_routes      import router as report_router
from app.community.routes.credibility_routes import router as credibility_router
from app.community.routes.cluster_routes     import router as cluster_router
from app.community.routes.intelligence_routes import router as intelligence_router
from app.community.routes.alert_routes        import router as alert_router
from app.community.routes.case_routes         import router as case_router

__all__ = [
    "user_router", "report_router", "credibility_router",
    "cluster_router", "intelligence_router", "alert_router",
    "case_router"
]
