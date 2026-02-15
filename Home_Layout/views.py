from django.shortcuts import render

def home_page(request):
    # เพิ่มข้อมูลจำลองเพื่อให้หน้า home_preview.html แสดงการ์ดวิจัย
    context = {
        'researches': [
            {'title': 'เด็กๆชอบกินอะไรที่LH4', 'description': 'Project description: วิจัยเกี่ยวกับอาหารที่นิสิตชอบซื้อกินที่ LH4', 'created_at': '15 Aug 2026'},
        ]
    }
    return render(request, 'home/home_preview.html', context)

def edit_profile(request):
    return render(request, 'home/edit_profile.html') # เช็คชื่อ Path folder ให้ถูก

def settings_view(request):
    return render(request, 'home/settings.html')

# Create your views here.
