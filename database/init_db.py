# database/init_db.py

from database.connection import get_connection


def init_db():

    connection = get_connection()

    cursor = connection.cursor()

    print("Initializing database...")

    # -----------------------------
    # Create gamblers table
    # -----------------------------

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

    # -----------------------------
    # Create betting_preferences table
    # -----------------------------

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

    # -----------------------------
    # Create stake_transactions table
    # -----------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stake_transactions (

            id INT AUTO_INCREMENT PRIMARY KEY,

            gambler_id INT NOT NULL,

            bet_id INT,

            transaction_type VARCHAR(50),

            amount DOUBLE,

            balance_after DOUBLE,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            INDEX idx_gambler (gambler_id),

            FOREIGN KEY (gambler_id)
            REFERENCES gamblers(id)

        )
        """
    )

    # -----------------------------
    # Create bets table
    # -----------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bets (

            bet_id VARCHAR(36) PRIMARY KEY,

            gambler_id INT NOT NULL,

            bet_amount DOUBLE NOT NULL,

            win_probability DOUBLE NOT NULL,

            odds DOUBLE DEFAULT 1.0,

            stake_before DOUBLE NOT NULL,

            stake_after DOUBLE,

            outcome VARCHAR(20),

            actual_winnings DOUBLE DEFAULT 0,

            is_settled BOOLEAN DEFAULT FALSE,

            session_id VARCHAR(36),

            strategy_name VARCHAR(50),

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

            INDEX idx_gambler (gambler_id),

            INDEX idx_session (session_id),

            FOREIGN KEY (gambler_id)
            REFERENCES gamblers(id)

        )
        """
    )

    # -----------------------------
    # Create betting_sessions table
    # -----------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS betting_sessions (

            session_id VARCHAR(36) PRIMARY KEY,

            gambler_id INT NOT NULL,

            initial_stake DOUBLE NOT NULL,

            current_stake DOUBLE NOT NULL,

            strategy_name VARCHAR(50),

            status VARCHAR(50) DEFAULT 'active',

            total_bets INT DEFAULT 0,

            total_wins INT DEFAULT 0,

            total_losses INT DEFAULT 0,

            win_rate_percentage DOUBLE DEFAULT 0,

            roi_percentage DOUBLE DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            ended_at TIMESTAMP NULL,

            INDEX idx_gambler (gambler_id),

            FOREIGN KEY (gambler_id)
            REFERENCES gamblers(id)

        )
        """
    )

    # -----------------------------
    # Create game_sessions table
    # -----------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS game_sessions (

            session_id VARCHAR(36) PRIMARY KEY,

            gambler_id INT NOT NULL,

            initial_stake DOUBLE NOT NULL,

            current_stake DOUBLE NOT NULL,

            upper_limit DOUBLE NOT NULL,

            lower_limit DOUBLE NOT NULL,

            min_bet DOUBLE NOT NULL,

            max_bet DOUBLE NOT NULL,

            max_games INT NOT NULL,

            strategy_name VARCHAR(50),

            status VARCHAR(50) DEFAULT 'active',

            end_reason VARCHAR(100),

            game_count INT DEFAULT 0,

            total_wins INT DEFAULT 0,

            total_losses INT DEFAULT 0,

            total_amount_wagered DOUBLE DEFAULT 0,

            total_amount_won DOUBLE DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            started_at TIMESTAMP NULL,

            ended_at TIMESTAMP NULL,

            INDEX idx_gambler (gambler_id),

            FOREIGN KEY (gambler_id)
            REFERENCES gamblers(id)

        )
        """
    )

    # -----------------------------
    # Create game_records table
    # -----------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS game_records (

            id INT AUTO_INCREMENT PRIMARY KEY,

            session_id VARCHAR(36) NOT NULL,

            gambler_id INT NOT NULL,

            game_number INT NOT NULL,

            bet_amount DOUBLE NOT NULL,

            outcome VARCHAR(20) NOT NULL,

            winnings DOUBLE DEFAULT 0,

            stake_before DOUBLE NOT NULL,

            stake_after DOUBLE NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            INDEX idx_session (session_id),

            INDEX idx_gambler (gambler_id),

            FOREIGN KEY (session_id)
            REFERENCES game_sessions(session_id),

            FOREIGN KEY (gambler_id)
            REFERENCES gamblers(id)

        )
        """
    )

    connection.commit()

    cursor.close()

    connection.close()

    print("Database initialized successfully.")