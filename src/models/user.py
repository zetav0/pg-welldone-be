import uuid

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        unique=True,
        editable=False,
        default=uuid.uuid4,
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class User(BaseModel):
    class Meta(BaseModel.Meta):
        db_table = "user"

    email = models.EmailField()
    full_name = models.CharField(max_length=250)
    document_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)


class Role(BaseModel):
    class Meta(BaseModel.Meta):
        db_table = "role"

    name = models.CharField(max_length=250)
    user = models.ForeignKey(User, related_name="roles", on_delete=models.CASCADE)


class Permission(BaseModel):
    class Meta(BaseModel.Meta):
        db_table = "permission"

    name = models.CharField(max_length=250)
    role = models.ForeignKey(Role, related_name="permissions", on_delete=models.CASCADE)
