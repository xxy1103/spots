from app.app import app


if __name__ == "__main__":
    app.run(debug=True)

# True 为调试模式，可以动态加载前端
# False 为生产模式，不能动态加载前端
