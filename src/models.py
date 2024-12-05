from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

# enum --> enumciado
class Genders(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    gender = db.Column(db.Enum(Genders), nullable=False)

    todos = db.relationship("Todos", back_populates="user", cascade="all, delete", uselist=True)


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "todos": list(map(lambda item: item.serialize(), self.todos))
        }


class Todos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(255), nullable=True)
    is_done = db.Column(db.Boolean(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user = db.relationship("User", back_populates="todos")


    def serialize(self):
        return {
            "id": self.id,
            "label": self.label,
            "is_done": self.is_done
        }
