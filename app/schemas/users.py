from pydantic import BaseModel


class AppUser(BaseModel):
    user_id: str
    full_name: str
    role: str
    business_unit: str
