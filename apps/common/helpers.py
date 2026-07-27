from django.core.paginator import Paginator as DjangoPaginator
from django.db import models


class PaginationHelper:
    """Helper for paginated querysets."""

    @staticmethod
    def paginate(queryset, page: int = 1, page_size: int = 20):
        """Paginate a queryset and return results with metadata."""
        paginator = DjangoPaginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        return {
            "results": list(page_obj.object_list),
            "page": page,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "total_count": paginator.count,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        }


class ValidationHelper:
    """Helper for common validation operations."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation."""
        from django.core.validators import validate_email as django_validate_email
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            django_validate_email(email)
            return True
        except DjangoValidationError:
            return False

    @staticmethod
    def validate_slug(slug: str) -> bool:
        """Validate a slug string."""
        import re
        return bool(re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug))


def generate_unique_slug(model, base_slug: str, organization=None) -> str:
    """Generate a unique slug for a model instance."""
    queryset = model.objects.all()
    if organization:
        queryset = queryset.filter(organization=organization)
    
    slug = base_slug
    counter = 1
    while queryset.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug
