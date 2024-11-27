from pathlib import Path
import pandas as pd

app_dir = Path(__file__).parent
tips = pd.read_csv(app_dir / "tips.csv")

# MODIFY TIP VALUES TO BE MORE REALISTIC #

# Step 1: Double every value in the total_bill column
tips['total_bill'] = tips['total_bill'] * 2

# Step 2: Double every 10th value in the tip column (in this case, the 10th value is at index 9)
tips.iloc[9, tips.columns.get_loc('tip')] *= 2

# Step 3: Increase every value in the tip column by 2.7
tips['tip'] = tips['tip'] * 2.7

# Step 2: Double every 16th value in the tip column (in this case, the 14th value is at index 12)
tips.iloc[15, tips.columns.get_loc('tip')] *= 2

# Decrease every 8th tip by 25%
tips.loc[tips.index % 8 == 7, 'tip'] *= 0.75  # Reduce by 25%

# Round the 'tip' column to 2 decimal places
tips['tip'] = tips['tip'].round(2)

# Remove the 'smoker' column
tips = tips.drop(columns=['smoker'])

# Add a new column for tip percentage (rounded to 2 decimal places)
tips['tip_percentage'] = ((tips['tip'] / tips['total_bill']) * 100).round(2)

print(tips)

