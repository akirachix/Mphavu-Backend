

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from teams.models import Team, Player
from .serializers import TeamSerializer, PlayerSerializer

class TeamListCreate(APIView):
    def get(self, request):
        queryset = Team.objects.all()
        name = request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        serializer = TeamSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Team added successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeamDetail(APIView):
    def get(self, request, pk):
        team = Team.objects.filter(pk=pk)
        if team.exists():
            serializer = TeamSerializer(team.first())
            return Response(serializer.data)
        return Response({'error': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)

class PlayerListCreate(APIView):
    def get(self, request, team_id):
        queryset = Player.objects.filter(team_id=team_id)
        serializer = PlayerSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, team_id):
        data = request.data.copy()
        data['team'] = team_id
        serializer = PlayerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Player added successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PlayerDetail(APIView):
    def get(self, request, pk):
        player = Player.objects.filter(pk=pk)
        if player.exists():
            serializer = PlayerSerializer(player.first())
            return Response(serializer.data)
        return Response({'error': 'Player not found'}, status=status.HTTP_404_NOT_FOUND)
