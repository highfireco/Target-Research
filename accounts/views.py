from django.shortcuts import render, redirect

def signup(request):
    error = ""

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            error = "Passwords do not match"
            return render(request, "signup.html", {"error": error})

        try:
            user = auth.create_user_with_email_and_password(email, password)
            uid = user["localId"]

            db.child("users").child(uid).set({
                "name": name,
                "email": email
            })

            return redirect("login")

        except Exception as e:
            print("FIREBASE ERROR:", e)
            error = str(e)

    return render(request, "signup.html", {"error": error})


def login_view(request):
    error = ""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            request.session["uid"] = user["localId"]
            return redirect("home")
        except:
            error = "Invalid email or password"
    return render(request, "login.html", {"error": error})


def home(request):
    if "uid" not in request.session:
        return redirect("login")

    uid = request.session["uid"]
    user = db.child("users").child(uid).get().val()

    return render(request, "home.html", {"name": user["name"]})


def logout(request):
    request.session.flush()
    return redirect("login")