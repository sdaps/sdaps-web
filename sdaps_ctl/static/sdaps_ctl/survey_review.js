(function() {
  'use strict';

  angular.module('sdaps', [])

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


  .controller('reviewCtrl', ['$scope', '$http', function($scope, $http) {

    $scope.preload_sheets = 2;

    $scope.image_base = window.image_base;
    $scope.sheet_base = window.sheet_base;
    $scope.review_sheets = window.review_sheets;


    $scope.options = {
      // XXX: Debouncer is not working!
      updateOn: 'default blur',
      debounce: {'default': 500, 'blur': 0},
    };

    $scope.current_sheet = -1;
    $scope.current_image = 0;
    $scope.sheets = {};

    $scope.imageRotation = function(img) {
        if (img && img['rotated'])
            return '180';
        else
            return '0';
    }

    $scope.imageSource = function(img) {
        if (img && img['image'])
            return $scope.image_base + img['image'] + '/' + img['image_page'];
        else
            return '';
    }

    $scope.getCurrentMatrix = function() {
        var sheet = this.sheets[$scope.current_sheet];
        if (!sheet || !sheet['images'])
            return '1, 0, 0, 0, 1, 0';
        var image = sheet['images'][$scope.current_image];
        if (!image)
            return '1, 0, 0, 0, 1, 0';
        var matrix = image['mmtopx'];

        if (_.isArray(matrix))
            return matrix.join(', ');
        else
            return '1, 0, 0, 0, 1, 0';
    }

    $scope.setCurrentSheet = function(sheet) {
        var sheets = []
        var start = sheet - $scope.preload_sheets;
        var stop = sheet + $scope.preload_sheets;

        if (sheet < 0)
            sheet = 0;
        if (sheet >= $scope.review_sheets)
            sheet = $scope.review_sheets - 1;

        if ($scope.current_sheet == sheet) {
            /* Nothing to do. */
            return;
        }

        $scope.current_sheet = sheet;

        if (start < 0)
          start = 0;
        if (stop >= $scope.review_sheets)
          stop = $scope.review_sheets - 1;

        /* Prune all other sheets */
        for (var i = start; i <= stop; i++) {
          sheets.push(i);
        }

        _.each($scope.sheets, function(sheet, key, data) {
          if (_.contains(sheets, parseInt(key, 10)))
            return;

          /* Delete any really old sheets. */
          /* XXX: Ensure data is posted! */
          delete $scope.sheets[key];
        });

        var existing_sheets = _.keys($scope.sheets);
        _.each(sheets, function(sheet, index, list) {
          /* Nothing to do if everything is already queued anyways. */
          if (_.contains(existing_sheets, sheet.toString()))
            return;

          $scope.sheets[sheet] = { '$loading' : true, 'images' : [], 'data' : {} };

          $http.get($scope.sheet_base + sheet, {'sheet' : sheet }).success(function(data, status, headers, config) {
            $scope.sheets[config['sheet']] = data;
            if (config['sheet'] == $scope.current_sheet) {
                if ($scope.current_image == -1) {
                    $scope.current_image = data['images'].length - 1;
                }
            }
          });
        });
    }

    $scope.next = function() {
        var sheet = $scope.sheets[$scope.current_sheet];
        if (sheet['$loading'])
            return;

        var next_sheet = $scope.current_sheet;
        var next_image = $scope.current_image + 1;

        if (next_image >= sheet['images'].length) {
            next_image = 0;
            next_sheet += 1;
            if (next_sheet >= $scope.review_sheets) {
                /* TODO: Alert or something. */
                return;
            }
        }
        $scope.current_image = next_image;
        $scope.setCurrentSheet(next_sheet);
    }

    $scope.prev = function() {
        var sheet = $scope.sheets[$scope.current_sheet];
        if (sheet['$loading'])
            return;

        var next_sheet = $scope.current_sheet;
        var next_image = $scope.current_image - 1;

        if (next_image < 0) {
            next_sheet -= 1;
            if (next_sheet < 0) {
                /* TODO: Alert or something. */
                return;
            }
            next_image = -1;
            if (!$scope.sheets[next_sheet]['loading']) {
                next_image = $scope.sheets[next_sheet]['images'].length - 1;
            }
        }
        $scope.current_image = next_image;
        $scope.setCurrentSheet(next_sheet);
    }


//    $scope.last_post_data = [];

//    $scope.update_server = _.debounce(function() {
//      $http.post($scope.data_url, $scope.data).success(function(data, status, headers, config) {
//          if (window.preview) {
//            /* Tell the preview that we expect an update soon (wait a maximum of 20s). */
//            window.preview.expect_update(20000);
//          }
//        });
//    }, 1000);

//    /* Add watch after first update. */
//    $scope.$watch('data', function(newVal, oldVal) {
//      if (newVal !== oldVal) {
//        $scope.update_server();
//      }
//    }, true);

    $scope.setCurrentSheet(0);

  }]);

})();


