'use strict'; //ensures that code is safe

var vocabApp = angular.module('vocabApp', ['ngRoute']);

vocabApp.config(function($routeProvider) {
      $routeProvider

            .when('/',{
                templateUrl: '/static/partials/index.html',
                controller: 'mainController'
            })
            .when('/about', {
                templateUrl: '/static/partials/about.html'
            })
            .otherwise({
              redirectTo: '/'
            });
});

vocabApp.controller('mainController',
  function($scope, $http){
      $scope.name = 'Ahmed Zaidi!';
      $scope.findLevel = function(){
        var word = $scope.word;
        $scope.level = word;
        $http({
          method:"POST",
          url: "http://127.0.0.1:8080/level",
          headers: {'Content-Type': undefined},
          data: word
        }).success(function(data){
            $scope.level = data
        });
        $http({
          method:"POST",
          url: "http://127.0.0.1:8080/word_stats",
          headers: {'Content-Type': undefined},
          data: word
        }).success(function(data){
            $scope.word_stats = data
        });
        $http({
          method:"POST",
          url: "http://127.0.0.1:8080/return_word_table",
          headers: {'Content-Type': undefined},
          data: word
        }).success(function(data){
            $scope.word_table = data
        });
      }
      $scope.curr_imgLoad = function(){
        $http({
          method:"POST",
          url: "http://127.0.0.1:8080/curr_imgLoad",
          headers: {'Content-Type': undefined},
        }).success(function(data){
            $scope.image_src = data
        });
      }

      $scope.imgLoad = function(){
        $http({
          method:"POST",
          url: "http://127.0.0.1:8080/imgLoad",
          headers: {'Content-Type': undefined},
        }).success(function(data){
            $scope.image_src = data
            $scope.feedback = ""
        });
        $http({
          method:"POST",
          url: "http://127.0.0.1:8080/quiz_word",
          headers: {'Content-Type': undefined}
        }).success(function(data){
            $scope.word_table = data
        });
      }

      $scope.runQuiz = function(){
        $scope.col_level = ['A1','A2','B1','B2','C1','C2']
        $scope.word_status = ['Active','Inactive']
        $http({
          method:"POST",
          url: "http://127.0.0.1:8080/quiz",
          headers: {'Content-Type': undefined}
        }).success(function(data){
            $scope.qtable = data
        });
        $http({
          method:"POST",
          url: "http://127.0.0.1:8080/quiz_level",
          headers: {'Content-Type': undefined}
        }).success(function(data){
            $scope.curr_level = data
        });
        $http({
          method:"POST",
          url: "http://127.0.0.1:8080/quiz_word",
          headers: {'Content-Type': undefined}
        }).success(function(data){
            $scope.word_table = data
        });
      }

      $scope.resetQuiz = function(){
        $scope.col_level = ['A1','A2','B1','B2','C1','C2']
        $scope.word_status = ['Active','Inactive']
        $http({
          method:"POST",
          url: "http://127.0.0.1:8080/r_quiz",
          headers: {'Content-Type': undefined}
        }).success(function(data){
            $scope.qtable = data
            $scope.feedback = ""
            $scope.answer = ""
        });
        $http({
          method:"POST",
          url: "http://127.0.0.1:8080/r_word",
          headers: {'Content-Type': undefined}
        }).success(function(data){
            $scope.word_table = data
        });
      }
      $scope.submitAns = function(){
        var answer = $scope.answer;
        $http({
          method:"POST",
          url: "http://127.0.0.1:8080/answer",
          headers: {'Content-Type': undefined},
          data: answer
        }).success(function(data){
            $scope.feedback = data
            $scope.answer = ""
        });
      }
});
