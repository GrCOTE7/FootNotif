from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware


class SubscriberCreate(BaseModel):
    email: EmailStr
    frequency: str


class SubscriptionCreate(BaseModel):
    email: EmailStr
    teams: List[str]

class SearchModel(BaseModel):
    query: List[str]

class SubscribersResponse(BaseModel):
    message: str
    subscribers: Optional[list] = None


class TeamResponse(BaseModel):
    name: str
    crest: str | None = None

class TeamsResponse(BaseModel):
    teams: list[TeamResponse]

class MessageResponse(BaseModel):
    message: str



def createApp(service):
    app = FastAPI(title="Football Match Notifier API")


    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://192.168.1.36:5173",
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=MessageResponse)
    def healthCheck():
        return {"message": "ok"}

    @app.get("/subscribers", response_model=SubscribersResponse)
    def listSubscribers():
        subscribers = service.getAllSubscribers()
        if subscribers is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch subscribers")
        return {"message": "Fetch successful", "subscribers": subscribers}

    @app.post("/subscribers", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
    def createSubscriber(subscriber: SubscriberCreate):
        msg = service.createSubscriber(email=subscriber.email, frequency=subscriber.frequency)
        if msg is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create subscriber")
        if "unique" in str(msg).lower() or "duplicate" in str(msg).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(msg))
        if "not found" in str(msg).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(msg))
        return {"message": str(msg)}

    @app.delete("/subscribers/{email}", response_model=MessageResponse)
    def deleteSubscriber(email: EmailStr):
        ok = service.deleteSubscriberByEmail(email)
        if ok is False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscriber not found or delete failed")
        return {"message": "Subscriber deleted"}

    @app.get("/subscribers/{email}/teams", response_model=TeamsResponse)
    def getSubscriberTeams(email: EmailStr):
        teams = service.getSubscriberTeams(email)
        if teams is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscriber not found")
        return {"teams": teams}


    @app.post("/subscriptions", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
    def createSubscriptions(payload: SubscriptionCreate):
        msg = service.createSubscriptions(email=payload.email, teams=payload.teams)
        if msg is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create subscriptions")
        if "subscriber not found" in str(msg).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(msg))
        if "no subscriptions" in str(msg).lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(msg))
        return {"message": str(msg)}

    @app.delete("/subscriptions/{email}/{teamName}", response_model=MessageResponse)
    def deleteSubscription(email: EmailStr, teamName: str):
        ok = service.deleteSubscriberTeam(subscriberEmail=email, teamName=teamName)
        if ok is False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found or delete failed")
        return {"message": "Subscription deleted"}

    @app.post("/notifications/send", response_model=dict)
    def sendNotificationsNow():
        result = service.sendToday()
        if result is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send notifications")
        if isinstance(result, str) and result.lower().startswith("error"):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result)
        return result
    
    @app.get("/teams/search", response_model=TeamsResponse)
    def searchTeams(q: str):
        teams = service.searchTeams(query=q)
        if teams is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search teams")
        if len(teams) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No results found")
        return {"teams": teams}


    return app