from database.init_db import init_db

from services.gambler_profile_service import (
    GamblerProfileService
)


def main():

    init_db()

    service = GamblerProfileService()

    gambler_id = service.create_gambler(

        name="John",

        email="john@email.com",

        initial_stake=1000,

        win_threshold=2000,

        loss_threshold=500
    )

    print(
        "Gambler created with ID:",
        gambler_id
    )

    service.update_preferences(

        gambler_id=gambler_id,

        min_bet=50,

        max_bet=500,

        strategy="Fixed"
    )

    gambler = service.get_gambler(
        gambler_id
    )

    print(
        "Current stake:",
        gambler["current_stake"]
    )

    service.reset_profile(
        gambler_id
    )

    print("Profile reset complete")


if __name__ == "__main__":

    main()