from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import os
from typing import List


app = FastAPI()

# Temporarily allow all origins to fix CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ct-frontend-production.up.railway.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",
    ],  # Explicitly include OPTIONS
    allow_headers=["*"],
    expose_headers=["*"],
)


class CoinTossRequest(BaseModel):
    choice: str  # "heads" or "tails"
    win_return: float = 0.5  # Default: +50% return
    lose_return: float = -0.4  # Default: -40% return
    current_wealth: float = 100.0


class SimulationRequest(BaseModel):
    num_tosses: int
    win_return: float = 0.5
    lose_return: float = -0.4
    simulation_type: str = "random"  # "random", "heads", "tails"


class GameState(BaseModel):
    wealth_history: List[float] = [100.0]
    round_number: int = 0
    total_wins: int = 0
    total_losses: int = 0


# In-memory game state (in production, you'd use a database)
game_states = {}


@app.get("/")
def read_root():
    return {"message": "Coin Toss Volatility Demo API"}


@app.post("/api/coin-toss/{player_id}")
def play_coin_toss(player_id: str, request: CoinTossRequest):
    try:
        # Get or create game state for this player
        if player_id not in game_states:
            game_states[player_id] = GameState()

        game_state = game_states[player_id]

        current_wealth = (
            request.current_wealth
            if request.current_wealth is not None
            else (game_state.wealth_history[-1] if game_state.wealth_history else 100.0)
        )

        # Flip the coin (50/50 chance)
        coin_result = random.choice(["heads", "tails"])

        # Determine if player won
        player_won = coin_result == request.choice.lower()

        # Calculate new wealth using return percentages
        current_wealth = request.current_wealth
        if player_won:
            new_wealth = current_wealth * (1 + request.win_return)
            game_state.total_wins += 1
        else:
            new_wealth = current_wealth * (1 + request.lose_return)
            game_state.total_losses += 1

        # Update game state
        game_state.round_number += 1
        game_state.wealth_history.append(new_wealth)

        # Calculate expected value for reference
        expected_value = 0.5 * (1 + request.win_return) + 0.5 * (
            1 + request.lose_return
        )

        return {
            "success": True,
            "data": {
                "coin_result": coin_result,
                "player_choice": request.choice.lower(),
                "player_won": player_won,
                "previous_wealth": current_wealth,
                "new_wealth": round(new_wealth, 2),
                "round_number": game_state.round_number,
                "total_wins": game_state.total_wins,
                "total_losses": game_state.total_losses,
                "wealth_history": [round(w, 2) for w in game_state.wealth_history],
                "expected_value": round(expected_value, 4),
                "win_return": request.win_return,
                "lose_return": request.lose_return,
            },
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/game-state/{player_id}")
def get_game_state(player_id: str):
    try:
        if player_id not in game_states:
            game_states[player_id] = GameState()

        game_state = game_states[player_id]
        current_wealth = (
            game_state.wealth_history[-1] if game_state.wealth_history else 100.0
        )

        return {
            "success": True,
            "data": {
                "current_wealth": round(current_wealth, 2),
                "round_number": game_state.round_number,
                "total_wins": game_state.total_wins,
                "total_losses": game_state.total_losses,
                "wealth_history": [round(w, 2) for w in game_state.wealth_history],
            },
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/simulate/{player_id}")
def simulate_multiple_tosses(player_id: str, request: SimulationRequest):
    try:
        # Reset game state for simulation
        game_states[player_id] = GameState()
        game_state = game_states[player_id]

        current_wealth = 100.0
        wins = 0
        losses = 0

        # Simulate all tosses based on simulation type
        for i in range(request.num_tosses):
            # Determine coin result and player choice based on simulation type
            coin_result = random.choice(["heads", "tails"])

            if request.simulation_type == "random":
                player_choice = random.choice(["heads", "tails"])  # Random choice
            elif request.simulation_type == "heads":
                player_choice = "heads"  # Always choose heads
            elif request.simulation_type == "tails":
                player_choice = "tails"  # Always choose tails
            else:
                player_choice = random.choice(["heads", "tails"])  # Default to random

            player_won = coin_result == player_choice

            # Calculate new wealth
            if player_won:
                current_wealth = current_wealth * (1 + request.win_return)
                wins += 1
            else:
                current_wealth = current_wealth * (1 + request.lose_return)
                losses += 1

            # Add to history
            game_state.wealth_history.append(current_wealth)

        # Update final game state
        game_state.round_number = request.num_tosses
        game_state.total_wins = wins
        game_state.total_losses = losses

        # Calculate expected value
        expected_value = 0.5 * (1 + request.win_return) + 0.5 * (
            1 + request.lose_return
        )

        return {
            "success": True,
            "data": {
                "final_wealth": round(current_wealth, 2),
                "total_rounds": request.num_tosses,
                "total_wins": wins,
                "total_losses": losses,
                "wealth_history": [round(w, 2) for w in game_state.wealth_history],
                "expected_value": round(expected_value, 4),
                "win_return": request.win_return,
                "lose_return": request.lose_return,
                "starting_wealth": 100.0,
                "simulation_type": request.simulation_type,
            },
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/reset-game/{player_id}")
def reset_game(player_id: str):
    try:
        game_states[player_id] = GameState()
        return {"success": True, "message": "Game reset successfully"}

    except Exception as e:
        return {"success": False, "error": str(e)}


# Add this for Railway deployment
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
