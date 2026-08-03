import pytest
from django.contrib.auth import get_user_model

from apps.organizations.models import Organization, Membership
from apps.clients.models import ClientCompany, Department
from apps.radar_templates.models import Template, TemplateVersion, TemplateApplication
from apps.radar_tasks.services import generate_tasks_from_application

User = get_user_model()


def _make_application(organization, client, stages, role_mappings, base_date="2026-01-01"):
    template = Template.objects.create(organization=organization, name="Template Teste")
    version = TemplateVersion.objects.create(
        organization=organization, template=template, version_number=1,
        name="v1", stages_snapshot=stages,
    )
    return TemplateApplication.objects.create(
        organization=organization, template=template, template_version=version,
        client=client, base_date=base_date, role_mappings=role_mappings,
    )


@pytest.mark.django_db
class TestGenerateTasksFromApplication:
    def test_assigns_task_to_member_mapped_to_department(self):
        organization = Organization.objects.create(name="Escritorio Teste")
        client = ClientCompany.objects.create(organization=organization, name="Cliente Teste")
        department = Department.objects.create(organization=organization, name="Fiscal")
        user = User.objects.create_user(email="responsavel@example.com", password="pass123")
        membership = Membership.objects.create(user=user, organization=organization)

        stages = [
            {"name": "Etapa 1", "tasks": [
                {"title": "Declarar imposto", "department": str(department.id)},
            ]},
        ]
        application = _make_application(
            organization, client, stages,
            role_mappings={f"dept_{department.id}": f"m-{membership.id}"},
        )

        created = generate_tasks_from_application(application)

        assert len(created) == 1
        task = created[0]
        assert task.assigned_to_id == user
        assert task.assigned_to == user.get_display_name()

    def test_assigns_task_to_member_mapped_to_role(self):
        organization = Organization.objects.create(name="Escritorio Teste")
        client = ClientCompany.objects.create(organization=organization, name="Cliente Teste")
        user = User.objects.create_user(email="fiscal@example.com", password="pass123")
        membership = Membership.objects.create(user=user, organization=organization)

        stages = [
            {"name": "Etapa 1", "tasks": [
                {"title": "Fechar balanco", "role": "Responsavel Fiscal"},
            ]},
        ]
        application = _make_application(
            organization, client, stages,
            role_mappings={"Responsavel Fiscal": f"m-{membership.id}"},
        )

        created = generate_tasks_from_application(application)

        assert len(created) == 1
        assert created[0].assigned_to_id == user

    def test_role_mapping_takes_precedence_over_department(self):
        organization = Organization.objects.create(name="Escritorio Teste")
        client = ClientCompany.objects.create(organization=organization, name="Cliente Teste")
        department = Department.objects.create(organization=organization, name="Fiscal")
        role_user = User.objects.create_user(email="role@example.com", password="pass123")
        dept_user = User.objects.create_user(email="dept@example.com", password="pass123")
        role_membership = Membership.objects.create(user=role_user, organization=organization)
        dept_membership = Membership.objects.create(user=dept_user, organization=organization)

        stages = [
            {"name": "Etapa 1", "tasks": [
                {"title": "Fechar balanco", "role": "Responsavel Fiscal", "department": str(department.id)},
            ]},
        ]
        application = _make_application(
            organization, client, stages,
            role_mappings={
                "Responsavel Fiscal": f"m-{role_membership.id}",
                f"dept_{department.id}": f"m-{dept_membership.id}",
            },
        )

        created = generate_tasks_from_application(application)

        assert len(created) == 1
        assert created[0].assigned_to_id == role_user

    def test_leaves_task_unassigned_when_no_mapping(self):
        organization = Organization.objects.create(name="Escritorio Teste")
        client = ClientCompany.objects.create(organization=organization, name="Cliente Teste")
        department = Department.objects.create(organization=organization, name="Fiscal")

        stages = [
            {"name": "Etapa 1", "tasks": [
                {"title": "Declarar imposto", "department": str(department.id)},
            ]},
        ]
        application = _make_application(organization, client, stages, role_mappings={})

        created = generate_tasks_from_application(application)

        assert len(created) == 1
        assert created[0].assigned_to_id is None
        assert created[0].assigned_to == ""
