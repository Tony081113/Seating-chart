import random
from termcolor import colored

rows, cols = 7, 6
empty_seats = {30, 31, 35}
male_numbers = set(range(1, 22))
female_numbers = set(range(22, 42)) - empty_seats

def seat_to_pos(seat_no):
    seat_no -= 1
    return seat_no // cols, seat_no % cols

def pos_to_seat(r, c):
    return r * cols + c + 1

def is_valid_pos(r, c):
    if 0 <= r < rows and 0 <= c < cols:
        seat_no = pos_to_seat(r, c)
        return seat_no not in empty_seats
    return False

def get_adjacent_positions(r, c):
    positions = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            nr, nc = r + dr, c + dc
            if (dr != 0 or dc != 0) and is_valid_pos(nr, nc):
                positions.append((nr, nc))
    return positions

def check_adjacent_gender(seat_matrix, pos, gender_set):
    for nr, nc in get_adjacent_positions(*pos):
        if seat_matrix[nr][nc] not in gender_set:
            return False
    return True

def try_fix_adjacent(seat_matrix, pos, gender_set):
    # 嘗試交換違規鄰座，優化男女鄰座條件
    r, c = pos
    for nr, nc in get_adjacent_positions(r, c):
        if seat_matrix[nr][nc] not in gender_set:
            # 找一個相反性別的座位交換
            for rr in range(rows):
                for cc in range(cols):
                    if (rr, cc) != (r, c) and (rr, cc) != (nr, nc):
                        if seat_matrix[rr][cc] in gender_set and seat_matrix[nr][nc] not in gender_set:
                            # 交換
                            seat_matrix[nr][nc], seat_matrix[rr][cc] = seat_matrix[rr][cc], seat_matrix[nr][nc]
                            # 交換完跳出
                            return True
    return False

def count_same_gender_adjacent(seat_matrix, r, c):
    count = 0
    current = seat_matrix[r][c]
    if current is None:
        return count
    gender_set = male_numbers if current in male_numbers else female_numbers
    for nr, nc in get_adjacent_positions(r, c):
        if seat_matrix[nr][nc] in gender_set:
            count += 1
    return count

def optimize_seating(seat_matrix, max_iter=1000):
    for _ in range(max_iter):
        total_same_gender = 0
        for r in range(rows):
            for c in range(cols):
                if is_valid_pos(r, c):
                    total_same_gender += count_same_gender_adjacent(seat_matrix, r, c)
        # 目標是減少total_same_gender
        improved = False
        for r1 in range(rows):
            for c1 in range(cols):
                for r2 in range(rows):
                    for c2 in range(cols):
                        if (r1, c1) != (r2, c2) and is_valid_pos(r1, c1) and is_valid_pos(r2, c2):
                            before = count_same_gender_adjacent(seat_matrix, r1, c1) + count_same_gender_adjacent(seat_matrix, r2, c2)
                            # 嘗試交換
                            seat_matrix[r1][c1], seat_matrix[r2][c2] = seat_matrix[r2][c2], seat_matrix[r1][c1]
                            after = count_same_gender_adjacent(seat_matrix, r1, c1) + count_same_gender_adjacent(seat_matrix, r2, c2)
                            # 如果改善，保留交換，否則還原
                            if after < before:
                                improved = True
                            else:
                                seat_matrix[r1][c1], seat_matrix[r2][c2] = seat_matrix[r2][c2], seat_matrix[r1][c1]
        if not improved:
            break
    return seat_matrix

def generate_seating(rows, cols, max_attempts=5000):
    available_numbers = [n for n in range(1, 42) if n not in empty_seats]
    possible_positions_21 = [(r, c) for r in range(1, rows - 1) for c in range(1, cols - 1) if is_valid_pos(r, c)]
    possible_positions_13_all = [(r, c) for r in range(1, rows - 1) for c in range(1, cols - 1) if is_valid_pos(r, c)]

    for attempt in range(max_attempts):
        seat_matrix = [[None for _ in range(cols)] for _ in range(rows)]

        pos_21 = random.choice(possible_positions_21)
        seat_matrix[pos_21[0]][pos_21[1]] = 21

        possible_positions_13 = [pos for pos in possible_positions_13_all if abs(pos[0] - pos_21[0]) > 2 or abs(pos[1] - pos_21[1]) > 2]
        if not possible_positions_13:
            continue

        pos_13 = random.choice(possible_positions_13)
        seat_matrix[pos_13[0]][pos_13[1]] = 13

        male_pool = list(male_numbers - {13, 21})
        female_pool = list(female_numbers)
        random.shuffle(male_pool)
        random.shuffle(female_pool)

        adj_21 = get_adjacent_positions(*pos_21)
        if len(adj_21) > len(male_pool):
            continue
        for r, c in adj_21:
            seat_matrix[r][c] = male_pool.pop()

        adj_13 = get_adjacent_positions(*pos_13)
        if len(adj_13) > len(female_pool):
            continue
        for r, c in adj_13:
            if seat_matrix[r][c] is None:
                seat_matrix[r][c] = female_pool.pop()

        used = {seat_matrix[r][c] for r in range(rows) for c in range(cols) if seat_matrix[r][c] is not None}
        remaining = [n for n in available_numbers if n not in used]
        male_remain = [n for n in remaining if n in male_numbers]
        female_remain = [n for n in remaining if n in female_numbers]
        random.shuffle(male_remain)
        random.shuffle(female_remain)

        for r in range(rows):
            for c in range(cols):
                if seat_matrix[r][c] is None and is_valid_pos(r, c):
                    if (r + c) % 2 == 0:
                        if male_remain:
                            seat_matrix[r][c] = male_remain.pop()
                        elif female_remain:
                            seat_matrix[r][c] = female_remain.pop()
                    else:
                        if female_remain:
                            seat_matrix[r][c] = female_remain.pop()
                        elif male_remain:
                            seat_matrix[r][c] = male_remain.pop()

        # 強制修正21, 13周圍，嘗試交換解決違規
        for _ in range(50):
            fixed_21 = check_adjacent_gender(seat_matrix, pos_21, male_numbers)
            fixed_13 = check_adjacent_gender(seat_matrix, pos_13, female_numbers)
            if fixed_21 and fixed_13:
                break
            if not fixed_21:
                try_fix_adjacent(seat_matrix, pos_21, male_numbers)
            if not fixed_13:
                try_fix_adjacent(seat_matrix, pos_13, female_numbers)

        # 最後優化整體座位同性別鄰座
        seat_matrix = optimize_seating(seat_matrix)

        if check_adjacent_gender(seat_matrix, pos_21, male_numbers) and check_adjacent_gender(seat_matrix, pos_13, female_numbers):
            return seat_matrix

    raise Exception(f"嘗試 {max_attempts} 次後無法生成符合條件的座位表")

def colorize(num):
    if num in male_numbers:
        return colored(f"{num:02}", "blue")
    else:
        return colored(f"{num:02}", "red")

if __name__ == "__main__":
    try:
        seat_matrix = generate_seating(rows, cols)
        for row in seat_matrix:
            print("\t".join(colorize(n) if n is not None else "  " for n in row))
    except Exception as e:
        print("錯誤:", e)
