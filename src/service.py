from datetime import datetime, timedelta

import bentoml
import jwt
import numpy as np
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

JWT_SECRET_KEY = "your_jwt_secret_key_here"
JWT_ALGORITHM = "HS256"

USERS = {"user123": "password123"}


class Credentials(BaseModel):
    username: str
    password: str


class AdmissionInput(BaseModel):
    gre_score: int = Field(ge=0, le=340)
    toefl_score: int = Field(ge=0, le=120)
    university_rating: int = Field(ge=1, le=5)
    sop: float = Field(ge=1, le=5)
    lor: float = Field(ge=1, le=5)
    cgpa: float = Field(ge=0, le=10)
    research: int = Field(ge=0, le=1)


def create_jwt_token(user_id: str) -> str:
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {"sub": user_id, "exp": expiration}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path.endswith("/predict"):
            token = request.headers.get("Authorization")
            if not token:
                return JSONResponse(
                    status_code=401, content={"detail": "Missing authentication token"}
                )
            try:
                token = token.split()[1]  # Bearer <token>
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                return JSONResponse(
                    status_code=401, content={"detail": "Token has expired"}
                )
            except jwt.InvalidTokenError:
                return JSONResponse(
                    status_code=401, content={"detail": "Invalid token"}
                )
            request.state.user = payload.get("sub")
        return await call_next(request)


@bentoml.service
class AdmissionModelService:
    def __init__(self):
        self.model = bentoml.sklearn.load_model("admission_lr:latest")

    @bentoml.api
    def predict_array(self, features: list[float]) -> list[float]:
        x = np.array(features, dtype=float).reshape(1, -1)
        pred = self.model.predict(x)
        return pred.tolist()


@bentoml.service
class AdmissionAPI:
    model_service = bentoml.depends(AdmissionModelService)

    @bentoml.api(route="/login")
    def login(self, credentials: Credentials):
        if USERS.get(credentials.username) == credentials.password:
            token = create_jwt_token(credentials.username)
            return {"token": token}

        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid credentials"},
        )

    @bentoml.api(route="/predict")
    def predict(self, input_data: AdmissionInput) -> dict:
        features = [
            input_data.gre_score,
            input_data.toefl_score,
            input_data.university_rating,
            input_data.sop,
            input_data.lor,
            input_data.cgpa,
            input_data.research,
        ]

        prediction = self.model_service.predict_array(features)
        return {"prediction": prediction}


# Register authentication middleware
AdmissionAPI.add_asgi_middleware(JWTAuthMiddleware)
