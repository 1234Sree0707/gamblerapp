# database/init_db.py

from database.connection import get_connection


def init_db():

    connection = get_connection()

    cursor = connection.cursor()

    print("Initializing database...")

    # Create gamblers table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS gamblers (

            id INT AUTO_INCREMENT PRIMARY KEY,

            name VARCHAR(100) NOT NULL,

            email VARCHAR(100),

            initial_stake DOUBLE,

            current_stake DOUBLE,

            win_threshold DOUBLE,

            loss_threshold DOUBLE,

            total_bets INT DEFAULT 0,

            total_wins INT DEFAULT 0,

            total_losses INT DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Create betting_preferences table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS betting_preferences (

            id INT AUTO_INCREMENT PRIMARY KEY,

            gambler_id INT UNIQUE,

            min_bet DOUBLE,

            max_bet DOUBLE,

            preferred_strategy VARCHAR(50),

            auto_play VARCHAR(10),

            session_limit INT,

            FOREIGN KEY (gambler_id)
            REFERENCES gamblers(id)
        )
        """
    )

    connection.commit()

    cursor.close()

    connection.close()

    print("Database initialized successfully.")