from uuid import uuid4

from app.models import Plan


plans =  [
    Plan(id=uuid4(), name="free",  price_in_cents=0, max_subjects_per_experiment=5000),
    Plan(id=uuid4(), name="developer",  price_in_cents=100*50, max_subjects_per_experiment=50000),
    Plan(id=uuid4(), name="team",  price_in_cents=100*250, max_subjects_per_experiment=100000),
    Plan(id=uuid4(), name="custom",  price_in_cents=100 * 1000, max_subjects_per_experiment=100000),
]
