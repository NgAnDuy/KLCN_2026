"""Vietnamese display names for exercises in the recommendation dataset."""


EXERCISE_NAMES_VI = {
    "Chạy interval": "Chạy bộ ngắt quãng",
    "Bodyweight Squat": "Ngồi xổm không tạ",
    "Wall Squat": "Ngồi xổm tựa tường",
    "Lunge": "Bước chùng chân",
    "Glute Bridge": "Nâng hông",
    "Calf Raise": "Nhón gót chân",
    "Push-up": "Chống đẩy",
    "Knee Push-up": "Chống đẩy chống gối",
    "Incline Push-up": "Chống đẩy trên bề mặt cao",
    "Plank": "Giữ tư thế tấm ván",
    "Side Plank": "Giữ tư thế tấm ván nghiêng",
    "Bird Dog": "Duỗi tay chân đối bên",
    "Dead Bug": "Duỗi tay chân đối bên khi nằm ngửa",
    "Mountain Climber": "Leo núi tại chỗ",
    "Burpee": "Bài tập toàn thân Burpee",
    "Dumbbell Goblet Squat": "Ngồi xổm ôm tạ đơn",
    "Dumbbell Row": "Kéo tạ đơn tập lưng",
    "Dumbbell Shoulder Press": "Đẩy tạ đơn qua đầu",
    "Dumbbell Chest Press": "Đẩy ngực với tạ đơn",
    "Romanian Deadlift nhẹ": "Gập hông nâng tạ kiểu Romania mức nhẹ",
    "Resistance Band Row": "Kéo dây kháng lực tập lưng",
    "Resistance Band Squat": "Ngồi xổm với dây kháng lực",
    "Bicep Curl": "Cuốn tạ tập tay trước",
    "Tricep Extension": "Duỗi tay sau với tạ",
    "Hatha Yoga": "Yoga Hatha",
    "Power Yoga": "Yoga cường độ cao",
    "Mobility toàn thân": "Vận động linh hoạt toàn thân",
    "Mobility hông": "Vận động linh hoạt khớp hông",
    "Mobility vai": "Vận động linh hoạt khớp vai",
    "Elliptical nhẹ": "Tập máy elip mức nhẹ",
    "Elliptical vừa": "Tập máy elip mức vừa",
    "Rowing Machine nhẹ": "Tập máy chèo thuyền mức nhẹ",
    "Rowing Machine vừa": "Tập máy chèo thuyền mức vừa",
    "Circuit Bodyweight cơ bản": "Tập liên hoàn không tạ cơ bản",
    "Circuit Bodyweight nâng cao": "Tập liên hoàn không tạ nâng cao",
    "Tai Chi": "Thái Cực Quyền",
    "Stretching phục hồi": "Giãn cơ phục hồi",
    "Dancing nhẹ": "Nhảy theo nhạc mức nhẹ",
    "Dancing aerobic": "Nhảy aerobic",
    "Badminton giải trí": "Cầu lông giải trí",
    "Chạy bộ nhẹ (Jogging)": "Chạy bộ nhẹ",
    "Chạy bộ đường dài (Endurance Run)": "Chạy bộ đường dài",
    "Chạy nước rút ngắt quãng (Sprint HIIT)": "Chạy nước rút ngắt quãng",
    "Pilates cốt lõi (Core Pilates)": "Pilates tập cơ lõi",
    "Chống đẩy cơ bản (Push-up)": "Chống đẩy cơ bản",
    "Chống đẩy nâng cao & Diamond Push-up": "Chống đẩy nâng cao và chống đẩy tay hình kim cương",
    "Gánh tạ đòn (Barbell Squat)": "Gánh tạ đòn",
    "Bước chùng chân với tạ đơn (Dumbbell Lunges)": "Bước chùng chân với tạ đơn",
    "Kéo xà đơn (Pull-up & Chin-up)": "Kéo xà đơn",
    "Nâng tạ đôi tập vai (Dumbbell Shoulder Press)": "Đẩy tạ đơn qua đầu tập vai",
    "Kéo cáp tập lưng xô (Lat Pulldown)": "Kéo cáp tập lưng xô",
    "Đẩy ngực với máy (Machine Chest Press)": "Đẩy ngực với máy",
    "Cuốn tạ đơn tập tay trước (Bicep Curl)": "Cuốn tạ đơn tập tay trước",
    "Tập cơ tay sau với dây cáp (Tricep Pushdown)": "Tập cơ tay sau với dây cáp",
    "Gập bụng kết hợp xoay eo (Russian Twist)": "Gập bụng kết hợp xoay eo",
    "Bài tập toàn thân Burpees HIIT": "Bài tập toàn thân Burpee ngắt quãng",
    "Leo núi tại chỗ (Mountain Climbers)": "Leo núi tại chỗ",
    "Bật nhảy mở rộng tay chân (Jumping Jacks)": "Bật nhảy dang tay chân",
    "Vung tạ ấm toàn thân (Kettlebell Swing)": "Vung tạ ấm toàn thân",
    "Nâng hông tập cơ mông (Glute Bridge & Hip Thrust)": "Nâng hông tập cơ mông",
    "Tập kháng lực với dây thun (Resistance Band)": "Tập kháng lực với dây thun",
    "Plank giữ thăng bằng cơ bụng": "Giữ tư thế tấm ván tập cơ bụng",
    "Giãn cơ động toàn thân (Dynamic Stretching)": "Giãn cơ động toàn thân",
}


def translate_exercise(name, language="vi"):
    """Translate a dataset exercise name for display without changing its ID."""
    if name is None:
        return ""
    name = str(name).strip()
    if language == "vi":
        return EXERCISE_NAMES_VI.get(name, name)
    return name
