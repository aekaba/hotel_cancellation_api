from pydantic import BaseModel
from typing import Literal

class PredictionInput(BaseModel):
    no_of_adults: int
    no_of_children: int
    no_of_weekend_nights: int
    no_of_week_nights: int
    required_car_parking_space: int
    lead_time: float
    arrival_year: int
    arrival_month: int
    arrival_date: int
    repeated_guest: int
    no_of_previous_cancellations: int
    no_of_previous_bookings_not_canceled: int
    avg_price_per_room: float
    no_of_special_requests: int

    # Kategorik: one-hot encode edilecekler
    type_of_meal_plan: Literal['Meal Plan 1', 'Meal Plan 2', 'Meal Plan 3', 'Not Selected']
    room_type_reserved: Literal['Room_Type 1', 'Room_Type 2', 'Room_Type 3', 'Room_Type 4', 'Room_Type 5', 'Room_Type 6', 'Room_Type 7']
    market_segment_type: Literal['Offline', 'Online', 'Corporate', 'Aviation', 'Complementary']