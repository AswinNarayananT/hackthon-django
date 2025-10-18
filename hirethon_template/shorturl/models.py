from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_organizations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Membership(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("editor", "Editor"),
        ("viewer", "Viewer"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    invited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "organization")

    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"


class Namespace(models.Model):
    name = models.SlugField(unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="namespaces")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class ShortURL(models.Model):
    namespace = models.ForeignKey(Namespace, on_delete=models.CASCADE, related_name="shorturls")
    shortcode = models.CharField(max_length=10)
    original_url = models.URLField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    click_count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_private = models.BooleanField(default=False)

    class Meta:
        unique_together = ("namespace", "shortcode")
        indexes = [
            models.Index(fields=["namespace", "shortcode"]),
        ]

    def __str__(self):
        return f"{self.namespace.name}/{self.shortcode} -> {self.original_url}"
