# core/service.py
from datetime import datetime, timedelta


class Service():
    def __init__(self, db, mailer, footballApi):
        self.db = db
        self.mailer = mailer
        self.footballApi = footballApi
        self.checkTeamsInDb()

    def checkTeamsInDb(self):
        isEmpty, err = self.db.isTeamsEmpty()
        if err is not None:
            print(err)
            return err

        if isEmpty is False:
            print("Teams already in database")
            return

        teams, err = self.footballApi.getTeams()
        if err is not None:
            print(f"Error fetching teams: {err}")
            return err

        success, err = self.db.upsertTeamsInfo(teams)
        if err is not None:
            print(f"Error inserting teams into DB: {err}")
            return err

        print(f"{len(teams)} teams inserted")

    def createSubscriber(self, email, frequency):
        frequency = (frequency or "").upper()
        err = self.db.insertSubscriber(email, frequency)
        if err is not None:
            print(f"Error creating subscriber email={email} err={err}")
            return str(err)
        return "Subscriber created successfully"

    def createSubscriptions(self, email, teams):
        subscriberId, err = self.db.getSubscriberIdByEmail(email)
        if err is not None or subscriberId is None:
            print(f"Error fetching subscriber id: {err}")
            return "Subscriber not found"

        created = 0

        for teamName in teams:
            teamId, err = self.db.getTeamIdByName(teamName)
            if err is not None or teamId is None:
                print(f"Error finding team '{teamName}': {err}")
                continue

            _, err = self.db.insertSubscription(subscriberId, teamId)
            if err is not None:
                print(f"Error creating subscription: {err}")
                continue

            created += 1

        if created == 0:
            return "No subscriptions created"
        return f"{created} subscription(s) created"

    def sendToday(self):
        isSunday = datetime.now().weekday() == 6
        frequencies = ["DAILY", "WEEKLY"] if isSunday else ["DAILY"]

        subscribers, err = self.db.getSubscribersByFrequencies(frequencies)
        if err is not None or subscribers is None:
            print(f"Error fetching subscribers: {err}")
            return f"Error fetching subscribers: {err}"

        sentTo = []

        for subscriber in subscribers:
            teamIds, err = self.db.getSubscriberTeamIds(subscriber["id"])
            if err is not None or not teamIds:
                continue

            now = datetime.now()
            startDate = now.strftime("%Y-%m-%d")
            delta = 1 if subscriber["frequency"] == "DAILY" else 7
            endDate = (now + timedelta(days=delta)).strftime("%Y-%m-%d")

            matchesEmail = []

            for teamId in teamIds:
                matches, err = self.footballApi.getMatchesBetweenDates(startDate, endDate, teamId)
                if err is not None:
                    print(f"Error fetching matches for team {teamId}: {err}")
                    return f"Error fetching matches for team {teamId}: {err}"

                if matches:
                    matchesEmail.extend(matches)

            if not matchesEmail:
                continue

            err = self.mailer.sendMail(matchesEmail, subscriber["email"])
            if err is not None:
                print(f"Error sending email: {err}")
                return f"Error sending email: {err}"

            sentTo.append(subscriber["email"])

        return {"sentTo": sentTo, "count": len(sentTo)}

    def getSubscriberTeams(self, subscriberEmail):
        subscriberId, err = self.db.getSubscriberIdByEmail(subscriberEmail)
        if err is not None or subscriberId is None:
            print("Error getting subscriber id from email")
            return None

        teams, err = self.db.getSubscriberTeams(subscriberId)
        if err is not None:
            print(f"Error getting subscriber teams: {err}")
            return None

        return teams


        return teamNames

    def deleteSubscriberTeam(self, subscriberEmail, teamName):
        subscriberId, err = self.db.getSubscriberIdByEmail(subscriberEmail)
        if err is not None or subscriberId is None:
            print("Error getting subscriber id from email")
            return False

        teamId, err = self.db.getTeamIdByName(teamName)
        if err is not None or teamId is None:
            print("Error getting team id from team name")
            return False

        err = self.db.deleteSubscription(subscriberId, teamId)
        if err is not None:
            return False

        return True

    def deleteSubscriberByEmail(self, subscriberEmail):
        subscriberId, err = self.db.getSubscriberIdByEmail(subscriberEmail)
        if err is not None or subscriberId is None:
            print("Error getting subscriber id from email")
            return False

        err = self.db.deleteSubscriber(subscriberId)
        if err is not None:
            return False

        return True

    def getAllSubscribers(self):
        subscribers, err = self.db.getAllSubscribers()
        if err is not None:
            print("Error fetching subscribers")
            return None
        return subscribers
    
    def searchTeams(self, query):
        rows, err = self.db.searchTeams(query)
        if err is not None:
            print(f"Error searching teams: {err}")
            return None
        return rows