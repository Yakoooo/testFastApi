from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.projectMember import ProjectMember
from app.models.user import User


# 查询有没有指定的关系表
def get_member(db: Session, project_id: int, user_id: int) -> ProjectMember | None:
    stmt = select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    )
    return db.scalar(stmt)

# 创建用户
def create_member(
    db: Session,
    project_id: int,
    user_id: int,
    role: str = "member",
) -> ProjectMember:
    member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=role,
    )
    db.add(member)
    return member

# 根据项目获取用户表。指定用户
def get_member_by_project_id(db: Session, project_id: int) -> list[User]:
    stmt = (
        select(User)
        .join(ProjectMember, ProjectMember.user_id == User.id)
        .where(ProjectMember.project_id == project_id)
    )
    # 根据用户信息表，从用户表获取用户
    return list(db.scalars(stmt).all())
