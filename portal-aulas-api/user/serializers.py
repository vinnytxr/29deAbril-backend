from user.models import User, Role, Invitation
from rest_framework import serializers
from courses.models import Course, ProgressCourseRelation
from lessons.models import Lesson
from lessons.serializers import LessonResumeSerializer, LessonSerializer
from courses.serializers.course import CourseResumeSerializer, ProgressCourseRelationSerializer
from . import services
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from collections.abc import Mapping
from collections import OrderedDict, defaultdict
from rest_framework.fields import get_error_detail, set_value
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.fields import (  # NOQA # isort:skip
    CreateOnlyDefault, CurrentUserDefault, SkipField, empty
)

from rest_framework.exceptions import APIException

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class UserSerializerForListProf(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'created')

class UserSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True)
    created_courses = serializers.SerializerMethodField()
    enrolled_courses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password', 'photo', 'about', 'contactLink', 'birth', 'cpf', 'role', 'enrolled_courses', 'created_courses', 'favorite_courses', 'created', 'modified')
        extra_kwargs = {'password': {'required': True}}
        
    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            message = self.error_messages['invalid'].format(
                datatype=type(data).__name__
            )
            print(message)
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='invalid')

        ret = OrderedDict()
        fields = self._writable_fields

        for field in fields:
            real_field_name = ""

            if field.field_name == "name":
                real_field_name = "Nome"
            elif field.field_name == "password":
                real_field_name = "Senha"
            elif field.field_name == "email":
                real_field_name = "E-mail"
            elif field.field_name == "birth":
                real_field_name = "Data de nascimento"
            elif field.field_name == "cpf":
                real_field_name = "CPF"
            elif field.field_name == "role":
                real_field_name = "Cargo"

            validate_method = getattr(self, 'validate_' + field.field_name, None)
            
            primitive_value = field.get_value(data)

            try:
                validated_value = field.run_validation(primitive_value)
                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except ValidationError as exc:
                if exc.detail[0].find("blank") != -1 or exc.detail[0].find("required") != -1:
                    raise serializers.ValidationError({'error': f"Campo '{real_field_name}' é obrigatório"}, code='invalid')
                elif exc.detail[0].find("valid") != -1:
                    raise serializers.ValidationError({'error': f"'{real_field_name}' inválido"}, code='invalid')
                elif exc.detail[0].find("already exists") != -1:
                    raise serializers.ValidationError({'error': f"'{real_field_name}' já utilizado"}, code='invalid')
                elif exc.detail[0].find("Date has wrong format") != -1:
                    raise serializers.ValidationError({'error': f"'{real_field_name}' inválida"}, code='invalid')
                elif exc.detail[0].find("at least 4") != -1:
                    raise serializers.ValidationError({'error': f"'{real_field_name}' precisa ter mais do que 3 caracteres"}, code='invalid')
                elif exc.detail[0].find("7 anos") != -1:
                    raise serializers.ValidationError({'error': "Usuário precisa ter 7 anos ou mais para realizar o cadastro"}, code='invalid')
                else:
                    raise serializers.ValidationError({'error': f"Campo: '{field.field_name}' Erro: {exc.detail[0]}"}, code='invalid')
            except SkipField:
                pass
            else:
                set_value(ret, field.source_attrs, validated_value)

        return ret

    def create(self, validated_data):
        password = validated_data.pop('password')
        role_ids = validated_data.pop('role')
        if not role_ids:
            raise serializers.ValidationError({'error': 'Usuário precisa ter um cargo'})
        user = User.objects.create_user(password=password, **validated_data)
        user.role.set(role_ids)
        return user
    
    def get_created_courses(self, obj):
        created_courses = Course.objects.filter(professor=obj)
        return CourseResumeSerializer(created_courses, many=True).data
    
    def get_enrolled_courses(self, obj):
        enrolled_course = obj.courses.all()
        serialized_courses_resume = CourseResumeSerializer(enrolled_course, many=True).data

        for serialized_course_resume in serialized_courses_resume:
            total = 0
            course_lessons_not_serialized = Lesson.objects.filter(course__id=serialized_course_resume["id"])
            course_lessons = LessonSerializer(course_lessons_not_serialized, many=True).data
            course_lessons_that_user_completed = [lesson for lesson in course_lessons if obj.id in lesson["users_who_completed"]]

            qtd_total_lessons = len(course_lessons)
            qtd_lessons_completed = len(course_lessons_that_user_completed)
            completed = (qtd_total_lessons == qtd_lessons_completed) and qtd_total_lessons != 0

            serialized_course_resume["total_lessons"] = qtd_total_lessons
            serialized_course_resume["lessons_completed"] = qtd_lessons_completed
            serialized_course_resume["completed"] = completed

            completed_percentage = 0
            if qtd_total_lessons > 0 and qtd_lessons_completed > 0:
                completed_percentage = int((qtd_lessons_completed/qtd_total_lessons) * 100) 

            serialized_course_resume["completed_percentage"] = completed_percentage

        return serialized_courses_resume

    def get_favorite_courses(self, obj):
        favorite_courses = obj.favorite_courses.all()
        return CourseResumeSerializer(favorite_courses, many=True).data
    
class UserResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']

class InvitationSerializer(serializers.ModelSerializer):

    professor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True)

    class Meta:
        model = Invitation
        fields = ['id', 'code', 'professor']

    def create(self, validated_data):
        code = validated_data.pop('code')
        code = services.create_invitation()

        invitation = Invitation.objects.create(code=code, **validated_data)
        return invitation

class ChangePasswordSerializer(serializers.ModelSerializer):
    model = User

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
        