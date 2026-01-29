users = {}
posts = []
post_id = 1

def create_user():
    while True:
        u = input("Username (no spaces): ").strip()
        if not u or " " in u or u in users:
            print("Invalid or taken.\n"); continue
        break
    users[u] = {"bio": input("Bio: ").strip(), "followers": 0}
    print("User created.\n")

def write_post():
    global post_id
    if not users: return print("No users.\n")
    u = input("Who is posting? ").strip()
    if u not in users: return print("User not found.\n")
    t = input("Post: ").strip()
    if not t: return print("Empty post.\n")
    posts.append({"id": post_id, "user": u, "text": t, "likes": 0})
    print(f"Post {post_id} created.\n")
    post_id += 1

def view_feed():
    if not posts: return print("No posts.\n")
    print("\n--- FEED ---")
    for p in posts:
        print(f"[{p['id']}] {p['user']}: {p['text']} ({p['likes']} likes)")
    print()

def like_post():
    if not posts: return print("No posts.\n")
    try: pid = int(input("Post ID: "))
    except: return print("Invalid.\n")
    for p in posts:
        if p["id"] == pid:
            p["likes"] += 1
            return print("Liked.\n")
    print("Not found.\n")

def search_feed():
    if not posts: return print("No posts.\n")
    q = input("Search: ").strip().lower()
    if not q: return print("Empty.\n")
    r = [p for p in posts if q in p["text"].lower()]
    if not r: return print("No matches.\n")
    for p in r: print(f"[{p['id']}] {p['user']}: {p['text']} ({p['likes']} likes)")
    print()

def show_top_post():
    if not posts: return print("No posts.\n")
    p = max(posts, key=lambda x: (x["likes"], -x["id"]))
    print(f"\nTop: [{p['id']}] {p['user']}: {p['text']} ({p['likes']} likes)\n")

def edit_bio():
    if not users: return print("No users.\n")
    u = input("User: ").strip()
    if u not in users: return print("Not found.\n")
    users[u]["bio"] = input("New bio: ")
    print("Updated.\n")

def delete_post():
    if not posts: return print("No posts.\n")
    u = input("Your username: ").strip()
    if u not in users: return print("Not found.\n")
    try: pid = int(input("Post ID: "))
    except: return print("Invalid.\n")
    for i, p in enumerate(posts):
        if p["id"] == pid:
            if p["user"] != u: return print("Not your post.\n")
            posts.pop(i); return print("Deleted.\n")
    print("Not found.\n")

def show_users():
    if not users: return print("No users.\n")
    for u, info in users.items():
        print(f"{u}: {info['bio']} ({info['followers']} followers)")
    print()

def main_menu():
    menu = """
1.Create user   2.Write post   3.View feed   4.Like post   5.Exit
6.Search        7.Top post     8.Edit bio    9.Delete post 10.Show users
"""
    funcs = {
        "1": create_user, "2": write_post, "3": view_feed, "4": like_post,
        "5": lambda: exit(), "6": search_feed, "7": show_top_post,
        "8": edit_bio, "9": delete_post, "10": show_users
    }
    while True:
        print(menu)
        f = funcs.get(input("Option: ").strip())
        f() if f else print("Invalid.\n")

if __name__ == "__main__":
    print("Welcome to TinyTwitter!")
    main_menu()
