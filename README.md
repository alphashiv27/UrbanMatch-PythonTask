# FastAPI User Management API (Updated Version)

## Overview
This application manages user profiles for a simple matchmaking system. You can create, read, update, and delete user profiles, as well as match users based on shared interests. Email addresses are validated, and a bulk user creation endpoint is provided for testing.

---

## Features
1. **Create User** (single or bulk)
2. **Read All Users** (with pagination)
3. **Read Single User by ID**
4. **Update User by ID**
5. **Delete User by ID**
6. **Match Users** based on interest criteria
7. **Email Validation** (regex-based)

---

## Installation
### Prerequisites
- Python 3.8+
- SQLite (bundled with Python)
- Recommended: a virtual environment

### Setup Steps
1. **Clone** the repository:
   ```bash
   git clone <repository_url>
   cd <project_directory>
   ```
2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   uvicorn urbanmatch.main:app --reload
   ```
5. **Open the interactive API docs**:
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Endpoints

### 1. Create a Single User
- **Endpoint:** `POST /users/`
- **Description:** Creates a new user.
- **Request Body (JSON):**
  ```json
  {
    "name": "Alice",
    "age": 25,
    "gender": "female",
    "email": "alice@example.com",
    "city": "New York",
    "interests": ["music", "reading"]
  }
  ```
- **Response:** Returns the created user object, or a 400 error if the email is invalid.

### 2. Bulk Create Users
- **Endpoint:** `POST /users/bulk`
- **Description:** Accepts an array of user objects to create multiple users at once.
- **Request Body (JSON):**
  ```json
  [
    {
      "name": "Bob",
      "age": 30,
      "gender": "male",
      "email": "bob@example.com",
      "city": "Chicago",
      "interests": ["sports", "travel"]
    },
    {
      "name": "Carol",
      "age": 28,
      "gender": "female",
      "email": "carol@example.com",
      "city": "Los Angeles",
      "interests": ["gaming", "photography"]
    }
  ]
  ```
- **Response:** Returns a list of the successfully created user objects. If any email is invalid, a 400 error is returned.

### 3. Read All Users
- **Endpoint:** `GET /users/`
- **Query Parameters:**
  - `skip`: How many records to skip (default: 0).
  - `limit`: Maximum number of records to return (default: 10).
- **Description:** Retrieves a list of users.
- **Response:** Returns an array of user objects.

### 4. Read Single User by ID
- **Endpoint:** `GET /users/{user_id}`
- **Description:** Fetches a user by ID.
- **Response:** Returns the user object or a 404 error if not found.

### 5. Update User by ID
- **Endpoint:** `PUT /users/{user_id}`
- **Description:** Updates an existing user.
- **Request Body (JSON):** Same structure as creating a user. Email must also be valid.
- **Response:** Returns the updated user object, or 404 if the user doesn’t exist.

### 6. Delete User by ID
- **Endpoint:** `DELETE /users/{user_id}`
- **Description:** Deletes a user by ID.
- **Response:** Returns the deleted user object, or 404 if not found.

### 7. Match Users
- **Endpoint:** `POST /match/{user_id}`
- **Description:** Finds users who match certain criteria relative to the user with `user_id`.
- **Request Body (JSON):**
  ```json
  {
    "city": ["New York", "Los Angeles"],
    "gender": ["male", "female"],
    "age_range_start": 20,
    "age_range_end": 35
  }
  ```
- **Matching Criteria:**
  - Users must be in any city listed in `city`.
  - Users must have a gender in `gender`.
  - Users must have an age between `age_range_start` and `age_range_end`.
  - Users must share **at least one** interest with the requesting user.
- **Response:** Returns a list of matching users.

### 8. Validate Email
- **Endpoint:** `GET /validate_email/{email}`
- **Description:** Validates an email address using a regex.
- **Response:**
  - `true` if valid.
  - `false` if invalid.

---

## Database Schema
Using SQLAlchemy with a SQLite backend. The `User` model (`models.py`) looks like:
```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    email = Column(String, unique=True, index=True)
    city = Column(String, index=True)
    interests = Column(MutableList.as_mutable(JSON))  # or a similar approach
```

### Schemas (`schemas.py`)
```python
class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    email: str
    city: str
    interests: List[str]

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class InterestFilter(BaseModel):
    city: List[str]
    gender: List[str]
    age_range_start: int
    age_range_end: int
```

---

## Testing
1. **Bulk Creation**: Use `POST /users/bulk` with a list of users.
2. **Read/Update/Delete**: Use the respective endpoints to ensure each operation works.
3. **Match**: Provide an `InterestFilter` JSON body to `/match/{user_id}`.
4. **Email Validation**: Test `GET /validate_email/{email}` with various email formats.

You can also write automated tests with a framework like **pytest**:
```bash
pytest
```

---

## License
This project is licensed under the MIT License.

## Author
Your Name — [LinkedIn Profile](https://www.linkedin.com)

---

This updated README reflects the latest endpoints and logic in the application, including the bulk user creation endpoint, the switch to a POST method for matching users, and the existing CRUD operations.

