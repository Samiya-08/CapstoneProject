from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth.models import User
from .models import Category, Tag, Article, Comment
from .serializers import (
    CategorySerializer, TagSerializer, ArticleSerializer, CommentSerializer,
    RegisterSerializer, ProfileSerializer
)


# Register View
@extend_schema(
    tags=['User Management'],
    request=RegisterSerializer,
    responses={201: RegisterSerializer}
)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User registered successfully!",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Profile ViewSet (CRUD)
@extend_schema(tags=['User Management'])
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def update(self, request, *args, **kwargs):
        # Faqat o'z profilini tahrirlash mumkin
        if request.user.id != int(kwargs.get('pk')):
            return Response(
                {"error": "You can only edit your own profile!"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Faqat o'z profilini o'chirish mumkin
        if request.user.id != int(kwargs.get('pk')):
            return Response(
                {"error": "You can only delete your own profile!"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


# Search View
@extend_schema(
    tags=['Search'],
    parameters=[
        OpenApiParameter(
            name='q',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Search by title or content',
            required=False
        ),
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Search by article ID',
            required=False
        ),
        OpenApiParameter(
            name='category',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by category name',
            required=False
        ),
        OpenApiParameter(
            name='tag',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by tag name',
            required=False
        )
    ]
)
class SearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        article_id = request.query_params.get('id', '')
        category_name = request.query_params.get('category', '')
        tag_name = request.query_params.get('tag', '')

        articles = Article.objects.filter(is_published=True)

        # Search by ID
        if article_id:
            try:
                article = articles.get(id=article_id)
                serializer = ArticleSerializer(article)
                return Response({
                    "count": 1,
                    "results": [serializer.data]
                })
            except Article.DoesNotExist:
                return Response({
                    "message": "Bunday ID'li maqola topilmadi"
                }, status=status.HTTP_404_NOT_FOUND)

        # Search by text (title or content)
        if query:
            articles = articles.filter(
                title__icontains=query
            ) | articles.filter(
                content__icontains=query
            )

        # Filter by category
        if category_name:
            articles = articles.filter(category__name__icontains=category_name)

        # Filter by tag
        if tag_name:
            articles = articles.filter(tags__name__icontains=tag_name)

        # Remove duplicates
        articles = articles.distinct()

        if articles.exists():
            serializer = ArticleSerializer(articles, many=True)
            return Response({
                "count": articles.count(),
                "results": serializer.data
            })
        else:
            return Response({
                "message": "Bunday maqola topilmadi. Boshqa so'z bilan qidiring."
            }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['Categories'])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


@extend_schema(tags=['Tags'])
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


@extend_schema(tags=['Articles'])
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save(update_fields=['views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@extend_schema(tags=['Comments'])
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)