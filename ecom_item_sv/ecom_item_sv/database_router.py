# class EcommerceRouter:
#     """
#     Điều hướng dữ liệu đến database phù hợp theo ứng dụng.
#     """
#     app_labels = {
#         'api': "mongodb",
#     }
#
#     def db_for_read(self, model, **hints):
#         """Chọn database cho các truy vấn đọc"""
#         return self.app_labels.get(model._meta.app_label, 'default')
#
#     def db_for_write(self, model, **hints):
#         """Chọn database cho các truy vấn ghi"""
#         return self.app_labels.get(model._meta.app_label, 'default')
#
#     def allow_relation(self, obj1, obj2, **hints):
#         """Cho phép quan hệ giữa các database"""
#         return None  # Mặc định không cho phép quan hệ giữa các DB khác nhau
#
#     def allow_migrate(self, db, app_label, model_name=None, **hints):
#         """Quyết định database nào sẽ nhận migration"""
#         if app_label in self.app_labels:
#             return db == self.app_labels[app_label]
#         return db == 'default'
