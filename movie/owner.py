from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class OwnerListView(ListView):
    """
    Sub-class the ListView to pass the request to the form.
    """


class OwnerDetailView(DetailView):
    """
    Sub-class the DetailView to pass the request to the form.
    """


class OwnerCreateView(LoginRequiredMixin, CreateView):
    """
    Sub-class of the CreateView to automatically pass the Request to the Form
    and add the owner to the saved object.
    """
    def form_valid(self, form):
        print('form_valid called')
        object = form.save(commit=False)
        object.owner = self.request.user
        object.save()
        return super(OwnerCreateView, self).form_valid(form)

class OwnerUpdateView(LoginRequiredMixin, UpdateView):
    """
    Sub-class the UpdateView to pass the request to the form and limit the
    queryset to the requesting user.
    """
    def get_queryset(self):
        print('update get_queryset called')
        qs = super(OwnerUpdateView, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerDeleteView(LoginRequiredMixin, DeleteView):
    def get_queryset(self):
        # ดึง queryset ทั้งหมด
        qs = super().get_queryset()
        # ถ้าเป็น superuser → คืนทุกอัน (admin ลบอะไรก็ได้)
        if self.request.user.is_superuser:
            return qs
        # ไม่งั้น → คืนเฉพาะของตัวเอง
        return qs.filter(owner=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        # object ยังไม่ได้ถูกลบ — ตรวจสอบสิทธิ์ก่อน
        obj = self.get_object()
        if obj.owner != request.user and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to delete this object.")
        return super().dispatch(request, *args, **kwargs)
