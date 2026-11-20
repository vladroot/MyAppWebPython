"""MongoDB user repository (mirrors C# UserRepository)."""

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase


class User:
    """MongoDB user document representation."""

    def __init__(
        self,
        id: Optional[str] = None,
        unique: str = "",
        name: str = "",
        age: int = 0,
    ) -> None:
        self.id = id
        self.unique = unique
        self.name = name
        self.age = age

    def __repr__(self) -> str:
        return f"User(id={self.id}, unique={self.unique!r}, name={self.name!r}, age={self.age})"


class IUserRepository:
    async def get_all(self) -> list[User]:
        raise NotImplementedError

    async def get_by_unique(self, unique: str) -> Optional[User]:
        raise NotImplementedError

    async def insert_one(self, user: User) -> None:
        raise NotImplementedError


class UserRepository(IUserRepository):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._users_collection = db.get_collection("users")

    async def get_all(self) -> list[User]:
        cursor = self._users_collection.find({})
        users: list[User] = []
        async for doc in cursor:
            users.append(
                User(
                    id=str(doc.get("_id")),
                    unique=doc.get("Unique", ""),
                    name=doc.get("Name", ""),
                    age=doc.get("Age", 0),
                )
            )
        return users

    async def get_by_unique(self, unique: str) -> Optional[User]:
        doc = await self._users_collection.find_one({"Unique": unique})
        if doc is None:
            return None
        return User(
            id=str(doc.get("_id")),
            unique=doc.get("Unique", ""),
            name=doc.get("Name", ""),
            age=doc.get("Age", 0),
        )

    async def insert_one(self, user: User) -> None:
        await self._users_collection.insert_one(
            {
                "Unique": user.unique,
                "Name": user.name,
                "Age": user.age,
            }
        )