from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import mysql.connector
from mysql.connector import Error
import os
from contextlib import contextmanager

app = FastAPI(
    title="Users CRUD API",
    description="A simple CRUD API for managing users",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration from environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME", "usersdb"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "ChangeMe123!")
}

# Pydantic models
class UserCreate(BaseModel):
    name: str
    mail: EmailStr

class UserUpdate(BaseModel):
    name: Optional[str] = None
    mail: Optional[EmailStr] = None

class UserResponse(BaseModel):
    id: int
    name: str
    mail: str

    class Config:
        from_attributes = True

# Database connection helper
@contextmanager
def get_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        yield connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")
    finally:
        if connection and connection.is_connected():
            connection.close()

# CRUD Operations

@app.get("/")
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")

@app.get("/api/users", response_model=List[UserResponse])
async def get_users():
    """Get all users"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, name, mail FROM users ORDER BY id")
            users = cursor.fetchall()
            cursor.close()
            return users
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get a user by ID"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, name, mail FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
    except HTTPException:
        raise
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@app.post("/api/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, mail) VALUES (%s, %s)",
                (user.name, user.mail)
            )
            conn.commit()
            user_id = cursor.lastrowid
            cursor.close()
            
            return {
                "id": user_id,
                "name": user.name,
                "mail": user.mail
            }
    except Error as e:
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@app.put("/api/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate):
    """Update a user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically based on provided fields
            updates = []
            values = []
            
            if user.name is not None:
                updates.append("name = %s")
                values.append(user.name)
            
            if user.mail is not None:
                updates.append("mail = %s")
                values.append(user.mail)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, values)
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
            
            cursor.close()
            
            # Fetch updated user
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, name, mail FROM users WHERE id = %s", (user_id,))
            updated_user = cursor.fetchone()
            cursor.close()
            
            return updated_user
    except HTTPException:
        raise
    except Error as e:
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@app.delete("/api/users/{user_id}", status_code=204)
async def delete_user(user_id: int):
    """Delete a user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
            
            cursor.close()
            return None
    except HTTPException:
        raise
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

