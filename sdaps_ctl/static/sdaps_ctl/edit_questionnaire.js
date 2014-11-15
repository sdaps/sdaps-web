(function() {
  'use strict';

  angular.module('sdaps', ['ui.tree'])

  .config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
  }])

  .filter('range', function() {
    return function(input, total) {
      total = parseInt(total);
      for (var i=0; i<total; i++)
        input.push(i);
      return input;
    };
  })

  .controller('questionnaireCtrl', ['$scope', '$http', function($scope, $http) {

    $scope.data_url = document.URL + '/questionnaire';

    $scope.remove = function(scope) {
      scope.remove();
    };

    $scope.newItem = function(type) {
      /* XXX: translations? */
      var defaults = {
        'multicol' : { 'columns' : 2 },
        'section' : { 'title' : 'Title', },
        'textbody' : { 'text' : 'Text', },
        'singlemark' : { 'question' : 'question', 'checkboxcount' : 5, 'lower' : 'a', 'upper' : 'b'},
        'choicequestion' : { 'question' : 'Question', 'columns' : 4 },
        'markgroup' : { 'heading' : 'Headline', 'checkboxcount' : 5 },
        'choicegroup' : { 'heading' : 'Headline' },
        'textbox' : { 'question' : 'Question', 'height' : 4.0, 'expand' : true},
        'choiceitem' : { 'answer' : 'Item', 'colspan' : 1 },
        'choiceitemtext' : { 'answer' : 'Item', 'colspan' : 2, 'height' : 1.2 },
        'markline' : { 'question' : 'Question', 'lower' : 'a', 'upper' : 'b' },
        'groupaddchoice' : { 'choice' : 'Choice' },
        'choiceline' : { 'Question' : 'question' },
      };

      var res = defaults[type];
      if (typeof res === 'undefined') {
        throw "Invalid object type or no type selected."
      }
      res['type'] = type;
      res['$editing'] = true;
      return res;
    }

    $scope.appendNewItem = function() {
      var objtype = document.getElementById("editor-new-type").value;
      if (!objtype)
        return;

      $scope.data.push($scope.newItem(objtype));
    };

    $scope.prependNewItem = function() {
      var objtype = document.getElementById("editor-new-type").value;
      if (!objtype)
        return;

      $scope.data = [$scope.newItem(objtype)].concat($scope.data);
    };

    $scope.appendNewSubItem = function(obj) {
      if (!obj.$newObjType)
        return;

      if (typeof obj.children === 'undefined')
        obj.children = [];

      obj.children.push($scope.newItem(obj.$newObjType));
      obj.$newObjType = undefined;

      obj.$adding = false;
    };

    $scope.prependNewSubItem = function(obj) {
      if (!obj.$newObjType)
        return;

      if (typeof obj.children === 'undefined')
        obj.children = [];

      obj.children = [$scope.newItem(obj.$newObjType)].concat(obj.children);
      obj.$newObjType = undefined;

      obj.$adding = false;
    };

    $scope.addChild = function(obj) {
      if (obj.$adding)
        obj.$adding = false;
      else
        obj.$adding = true;
    };

    $scope.parentAttr = function(scope, attr) {
      if (scope.$parentNodeScope)
        return scope.$parentNodeScope.$modelValue[attr];
      else
        return undefined;
    };

    $scope.canAdd = function(type) {
        return _.contains(['multicol', 'choicequestion', 'markgroup', 'choicegroup'], type);
    }

    $scope.editObj = function(obj) {
      obj.$editing = true;
    };

    $scope.doneEditingObj = function(obj) {
      obj.$editing = false;
    };

    $scope.saveObj = function(obj) {
      //obj.save();
    };

    $scope.removeObj = function(scope) {
      if (window.confirm('Are you sure to remove this object?')) {
        scope.remove();
      }
    };


    $scope.options = {
      // XXX: Debouncer is not working!
      updateOn: 'default blur',
      debounce: {'default': 500, 'blur': 0},
      accept: function(sourceNode, destNodes, destIndex) {
        var src = sourceNode.$modelValue;
        var dest = destNodes.$modelValue;

        var generic_types = ['multicol', 'section', 'textbody', 'singlemark', 'choicequestion', 'markgroup', 'choicegroup', 'textbox'];
        var subtypes = {
          'toplevel' : generic_types,
          'multicol' : generic_types,
          'choicequestion' : ['choiceitem', 'choiceitemtext'],
          'markgroup' : ['markline'],
          'choicegroup' : ['groupaddchoice', 'choiceline'],
        };

        var dest_type = '';

        if (typeof destNodes.$parent.$modelValue === 'undefined') {
            dest_type = 'toplevel';
        } else {
            dest_type = destNodes.$parent.$modelValue.type;
        }

        var src_type = src.type;

        return _.contains(subtypes[dest_type], src_type);
      },
    };

    $scope.data = [];

    $http.get($scope.data_url).success(function(data, status, headers, config) {
      $scope.data = data;
    });

    $scope.last_post_data = [];

    $scope.update_server = _.debounce(function() {
      $http.post($scope.data_url, $scope.data).success(function(data, status, headers, config) {
          if (window.preview) {
            /* Tell the preview that we expect an update soon (wait a maximum of 20s). */
            window.preview.expect_update(20000);
          }
        });
    }, 1000);

    /* Add watch after first update. */
    $scope.$watch('data', function(newVal, oldVal) {
      if (newVal !== oldVal) {
        $scope.update_server();
      }
    }, true);

  }]);

})();


