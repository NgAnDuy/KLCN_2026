import pandas as pd
import numpy as np

# =========================================================
# 1. ĐỌC DATASET GỐC
# =========================================================

INPUT_FILE = "health_dataset.csv"
OUTPUT_FILE = "dataset_clean.csv"

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("DATASET BAN ĐẦU")
print("=" * 60)
print("Số dòng :", df.shape[0])
print("Số cột  :", df.shape[1])


# =========================================================
# 2. CHUẨN HÓA TÊN CỘT
# =========================================================

df.columns = df.columns.str.strip()

# Xóa khoảng trắng trong dữ liệu text
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].str.strip()


# =========================================================
# 3. XỬ LÝ CÁC CỘT SỐ
# =========================================================

numeric_cols = [
    "age",
    "height_cm",
    "weight_kg",
    "bmi",
    "bmr",
    "tdee",
    "water_intake_l",
    "calories_consumed",
    "avg_steps_7d",
    "avg_active_minutes_7d",
    "avg_calories_burned_7d",
    "avg_exercise_minutes_7d",
    "exercise_sessions_7d",
    "avg_sleep_hours_7d"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# =========================================================
# 4. LOẠI BỎ USER_ID TRÙNG
# =========================================================

before = len(df)

df = df.drop_duplicates(
    subset=["user_id"],
    keep="first"
)

print("\nDuplicate user_id bị loại:",
      before - len(df))


# =========================================================
# 5. LOẠI BỎ DÒNG BỊ THIẾU DỮ LIỆU
# =========================================================

before = len(df)

df = df.dropna(
    subset=[
        "user_id",
        "age",
        "gender",
        "height_cm",
        "weight_kg",
        "goal"
    ]
)

print("Dòng thiếu dữ liệu bị loại:",
      before - len(df))


# =========================================================
# 6. LỌC TUỔI
# =========================================================

before = len(df)

df = df[
    (df["age"] >= 18) &
    (df["age"] <= 70)
]

print("Dòng tuổi không hợp lệ:",
      before - len(df))


# =========================================================
# 7. LỌC CHIỀU CAO
# =========================================================

before = len(df)

df = df[
    (df["height_cm"] >= 140) &
    (df["height_cm"] <= 210)
]

print("Dòng chiều cao không hợp lệ:",
      before - len(df))


# =========================================================
# 8. LỌC CÂN NẶNG
# =========================================================

before = len(df)

df = df[
    (df["weight_kg"] >= 40) &
    (df["weight_kg"] <= 150)
]

print("Dòng cân nặng không hợp lệ:",
      before - len(df))


# =========================================================
# 9. LỌC BMI
# =========================================================

before = len(df)

df = df[
    (df["bmi"] >= 14) &
    (df["bmi"] <= 45)
]

print("Dòng BMI không hợp lệ:",
      before - len(df))


# =========================================================
# 10. LỌC BMR
# =========================================================

before = len(df)

df = df[
    (df["bmr"] >= 900) &
    (df["bmr"] <= 3000)
]

print("Dòng BMR không hợp lệ:",
      before - len(df))


# =========================================================
# 11. LỌC TDEE
# =========================================================

before = len(df)

df = df[
    (df["tdee"] >= 1200) &
    (df["tdee"] <= 5000)
]

print("Dòng TDEE không hợp lệ:",
      before - len(df))


# =========================================================
# 12. LỌC WATER
# =========================================================

before = len(df)

df = df[
    (df["water_intake_l"] >= 1) &
    (df["water_intake_l"] <= 6)
]

print("Dòng water không hợp lệ:",
      before - len(df))


# =========================================================
# 13. LỌC CALORIES
# =========================================================

before = len(df)

df = df[
    (df["calories_consumed"] >= 1000) &
    (df["calories_consumed"] <= 5000)
]

print("Dòng calories không hợp lệ:",
      before - len(df))


# =========================================================
# 14. LỌC STEPS
# =========================================================

before = len(df)

df = df[
    (df["avg_steps_7d"] >= 500) &
    (df["avg_steps_7d"] <= 30000)
]

print("Dòng steps không hợp lệ:",
      before - len(df))


# =========================================================
# 15. LỌC ACTIVE MINUTES
# =========================================================

before = len(df)

df = df[
    (df["avg_active_minutes_7d"] >= 0) &
    (df["avg_active_minutes_7d"] <= 600)
]

print("Dòng active minutes không hợp lệ:",
      before - len(df))


# =========================================================
# 16. LỌC EXERCISE MINUTES
# =========================================================

before = len(df)

df = df[
    (df["avg_exercise_minutes_7d"] >= 0) &
    (df["avg_exercise_minutes_7d"] <= 600)
]

print("Dòng exercise minutes không hợp lệ:",
      before - len(df))


# =========================================================
# 17. LỌC EXERCISE SESSIONS
# =========================================================

before = len(df)

df = df[
    (df["exercise_sessions_7d"] >= 0) &
    (df["exercise_sessions_7d"] <= 14)
]

print("Dòng exercise sessions không hợp lệ:",
      before - len(df))


# =========================================================
# 18. LỌC SLEEP
# =========================================================

before = len(df)

df = df[
    (df["avg_sleep_hours_7d"] >= 4) &
    (df["avg_sleep_hours_7d"] <= 12)
]

print("Dòng sleep không hợp lệ:",
      before - len(df))


# =========================================================
# 19. KIỂM TRA GENDER
# =========================================================

valid_gender = [
    "Male",
    "Female"
]

before = len(df)

df = df[
    df["gender"].isin(valid_gender)
]

print("Dòng gender không hợp lệ:",
      before - len(df))


# =========================================================
# 20. KIỂM TRA ACTIVITY LEVEL
# =========================================================

valid_activity = [
    "Sedentary",
    "Moderate",
    "Active",
    "Very Active"
]

before = len(df)

df = df[
    df["activity_level"].isin(valid_activity)
]

print("Dòng activity không hợp lệ:",
      before - len(df))


# =========================================================
# 21. KIỂM TRA GOAL
# =========================================================

valid_goals = [
    "weight_loss",
    "weight_gain",
    "maintenance",
    "fitness_improvement",
    "healthy_lifestyle"
]

before = len(df)

df = df[
    df["goal"].isin(valid_goals)
]

print("Dòng goal không hợp lệ:",
      before - len(df))


# =========================================================
# 22. TÍNH LẠI BMI
# =========================================================

height_m = df["height_cm"] / 100

df["bmi"] = (
    df["weight_kg"] /
    (height_m ** 2)
).round(2)


# =========================================================
# 23. TÍNH LẠI BMR
# =========================================================

male = df["gender"] == "Male"
female = df["gender"] == "Female"

df.loc[male, "bmr"] = (
    10 * df.loc[male, "weight_kg"]
    + 6.25 * df.loc[male, "height_cm"]
    - 5 * df.loc[male, "age"]
    + 5
)

df.loc[female, "bmr"] = (
    10 * df.loc[female, "weight_kg"]
    + 6.25 * df.loc[female, "height_cm"]
    - 5 * df.loc[female, "age"]
    - 161
)

df["bmr"] = df["bmr"].round(0)


# =========================================================
# 24. TÍNH LẠI TDEE
# =========================================================

activity_factor = {
    "Sedentary": 1.20,
    "Moderate": 1.55,
    "Active": 1.725,
    "Very Active": 1.90
}

df["tdee"] = (
    df["bmr"] *
    df["activity_level"].map(activity_factor)
).round(0)


# =========================================================
# 25. KIỂM TRA LẠI NULL
# =========================================================

print("\n" + "=" * 60)
print("KIỂM TRA NULL")
print("=" * 60)

print(df.isnull().sum())


# =========================================================
# 26. KIỂM TRA DUPLICATE
# =========================================================

print("\n" + "=" * 60)
print("KIỂM TRA DUPLICATE")
print("=" * 60)

print(
    "Duplicate:",
    df.duplicated().sum()
)


# =========================================================
# 27. KIỂM TRA PHÂN BỐ GOAL
# =========================================================

print("\n" + "=" * 60)
print("PHÂN BỐ GOAL")
print("=" * 60)

print(
    df["goal"].value_counts()
)


# =========================================================
# 28. SẮP XẾP USER_ID
# =========================================================

df["user_number"] = (
    df["user_id"]
    .str.extract(r"(\d+)")
    .astype(int)
)

df = df.sort_values("user_number")

df = df.drop(columns=["user_number"])

df = df.reset_index(drop=True)


# =========================================================
# 29. LƯU DATASET SẠCH
# =========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# =========================================================
# 30. KẾT QUẢ CUỐI
# =========================================================

print("\n" + "=" * 60)
print("CLEAN DATASET HOÀN TẤT")
print("=" * 60)

print("Dataset ban đầu : 500 dòng")
print("Dataset sạch    :", len(df), "dòng")
print("Số cột          :", len(df.columns))

print("\nFile đã tạo:")
print(OUTPUT_FILE)

print("\n5 dòng cuối:")
print(df.tail())