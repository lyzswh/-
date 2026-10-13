from abc import ABC,abstractmethod
import json

#书籍类
class Book:
    def __init__(self, book_id,title, author, total_num):
        self.book_id = book_id#编号
        self.title = title#书籍名称
        self.author = author#书籍作者
        self.total_num = total_num#书籍数量
        self.__available_num=total_num#可用数量

    def borrow_book(self):
        if  self.__available_num>0:
            self.__available_num-=1
            return True
        else:
            return False

    def return_book(self):
        self.__available_num +=1

    def get_available_num(self):
        return self.__available_num

#抽象类:是一种只能被继承，不能被直接实例化的类，作用就是规定子类必须要实现哪些方法，强制子类必须遵守统一的代码规范
# Python中的抽象类，需要继承 abc 模块中的ABC类 ---> ABC:Abstract Base Class
#会员类
class Member(ABC):
    def __init__(self,member_id,name,password):
        self.member_id = member_id#ID
        self.name = name#姓名
        self.__password = password#密码
        self.__borrowed_books = []#借阅书籍列表

    #借书
    def borrow_book(self,book:Book):
        # 判断当前会员借阅数量是否达到最大限制
        if len(self.__borrowed_books)>=self.get_max_books():
            print("该会员书籍借阅数量已超过最大值")
            return False

        # 判断书籍是否可借阅，Book.borrow_book方法的返回值是True/False
        if book.borrow_book():
            self.__borrowed_books.append(book)
            print(f"{self.name},您成功借阅书籍--{book.title}")
            return True
        else:
            print(f"{self.name}，您借阅书籍失败，{book.title}已借完")
            return False
    #还书
    def return_book(self,book:Book):
        if book in self.__borrowed_books:
            # 还书
            book.return_book()
            self.__borrowed_books.remove(book)
            print(f"{self.name}已成功归还图书{book.title}")
        else:
            print(f"归还失败，您未借阅图书{book.title}")

    # 获取会员最大借阅数量(需要在子类中实现)
    @abstractmethod
    def get_max_books(self)->int:
        pass

    def get_borrowed_books(self):
        return self.__borrowed_books

    def get_password(self):
        return self.__password


class NormalMember(Member):
    def get_max_books(self)->int:
        return 3


class VipMember(Member):
    def __init__(self,member_id,name,password,vip_level):
        super().__init__(member_id, name, password)
        self.vip_level = vip_level # 会员等级

    def get_max_books(self)->int:
        return 6+self.vip_level

class LibrarySystem:
    def __init__(self):
        self.books = {}   # 书籍列表---> {"AI001":Book对象,"AI002":Book对象},
        self.members = {}  # 会员列表--->{"N001":Member对象，"N002":Member对象},
        self.current_member:Member|None = None #当前登录会员

        self.load_books_data()
        self.load_members_data()

    def load_books_data(self):
        with open("data/books.json","r",encoding="utf-8") as f:
            books_data = json.load(f)
            for book in books_data:
                self.books[book["编号"]]=Book(book["编号"],book["标题"],book["作者"],book["数量"])
            print("加载书籍数据成功")

    def load_members_data(self):
        with open("data/members.json","r",encoding="utf-8") as f:
            members_data = json.load(f)
            for member in members_data:
                if member['卡号'].startswith('N'):
                    self.members[member["卡号"]]=NormalMember(member["卡号"],member["姓名"],member["密码"])
                elif member["卡号"].startswith('V'):
                    self.members[member["卡号"]]=VipMember(member["卡号"],member["姓名"],member["密码"],member["会员等级"])
            print("加载会员数据成功")


    def login(self):
        for attempt in range(3):
            print("\n【登录】")
            member_id = input("请输入会员卡号:").strip()
            password = input("请输入会员密码:").strip()

            #检查会员卡号
            if member_id not in self.members:
                print("登录失败，会员卡号不存在!")
                continue

            #判断密码是否正确
            member=self.members[member_id]
            if member.get_password() == password:
                print(f"登录成功，欢迎您，{member.name}")
                self.current_member=member
                return True

            print("登录失败：密码错误！")

        print("连续输错三次，已退出登录。")
        return False



    def run(self):
        if self.login():
            while True:
                print("\n1.借阅图书")
                print("2.归还图书")
                print("3.查看借阅")
                print("4.退出系统")

                choice = input("请选择操作(1-4):")
                match choice:
                    case "1":
                        self.borrow_book()
                    case "2":
                        self.return_book()
                    case "3":
                        self.show_borrowed_books()
                    case "4":
                        print(f"{self.current_member.name},欢迎您的下次使用,BYE BYE~")
                        break
                    case _:
                        print("无效的选项，请重新选择!")

    def borrow_book(self):
        # 1.展示所有图书信息
        for book in self.books.values():# 取字典里的值（Book 对象）
            print(f"编号: {book.book_id},标题: {book.title},作者: {book.author}，总数: {book.total_num}，可用: {book.get_available_num()}")

        # 2.获取用户输入的图书编号，执行借书操作
        book_id=input("请输入借阅书籍的ID:")
        if book_id not in self.books:
            print("该书籍不存在")
            return
        self.current_member.borrow_book(self.books[book_id])
            
    def return_book(self):
        # 1.展示所借阅图书列表
        borrowed_books = self.current_member.get_borrowed_books()
        print("[已经借阅的图书列表:]")
        for book in borrowed_books:
            print(f"编号: {book.book_id},标题: {book.title}")

        # 2.获取用户输入的图书编号，执行借书操作
        book_id = input("请输入归还书籍的ID")
        if book_id not in self.books:
            print("还书失败，该书籍编号不存在")
            return
        self.current_member.return_book(self.books[book_id])

    def show_borrowed_books(self):
        borrowed_books = self.current_member.get_borrowed_books()
        if len(borrowed_books)>0:
            print("[已经借阅的图书列表:]")
            for book in borrowed_books:
                print(f"编号: {book.book_id},标题: {book.title}")
        else:
            print(f"{self.current_member.name},您未借阅书籍")


if __name__ == '__main__':
    ls=LibrarySystem()
    ls.run()
