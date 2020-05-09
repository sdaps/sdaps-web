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

    $scope.zoom_step = -4;
    $scope.zoom = Math.pow(1.2, $scope.zoom_step);

    $scope.options = {
      // XXX: Debouncer is not working!
      updateOn: 'default blur',
      debounce: {'default': 500, 'blur': 0},
    };

    $scope.current_sheet_num = 0;
    $scope.current_sheet = -1;
    $scope.current_image = 0;
    $scope.current_image_num = 1;
    $scope.sheets = {};

    $scope.genPrefixes = function(style) {
        var prefixes = ['', '-moz-', '-webkit-', '-ms-', '-o-', ''];
        return prefixes.join(style);
    }

    $scope.imageRotation = function(img) {
        if (img && img['rotated'])
            return 'transform: rotate(180deg);';
        else
            return 'transform: rotate(0deg);';
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
            return 'transform: matrix(1, 0, 0, 0, 1, 0);';
        var image = sheet['images'][$scope.current_image];
        if (!image)
            return 'transform: matrix(1, 0, 0, 0, 1, 0);';
        var matrix = image['mmtopx'];

        if (_.isArray(matrix))
            return 'transform: matrix('+matrix.join(', ')+') scale(0.01);';
        else
            return 'transform: matrix(1, 0, 0, 0, 1, 0);';
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

        /* submit the current sheet. */
        $scope.submitSheet($scope.current_sheet);

        $scope.current_sheet = sheet;
        $scope.current_sheet_num = $scope.current_sheet + 1;

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

          $http.get($scope.sheet_base + sheet, {'sheet' : sheet })
            .success(function(data, status, headers, config) {
              $scope.sheets[config['sheet']] = data;
              if (config['sheet'] == $scope.current_sheet) {
                  if ($scope.current_image == -1) {
                      $scope.current_image = data['images'].length - 1;
                  }
              }

              data['$dirty'] = false;
            })
            .error(function(data, status, headers, config) {
              $scope.sheets[sheet] = { '$loading' : false };
              alert("Server did not respond to request. Cannot review this sheet for now!");
            });
        });
    }

    $scope.$watch('current_sheet_num', function(newSheet, oldSheet) {
        if (newSheet != oldSheet) {
            $scope.setCurrentSheet($scope.current_sheet_num - 1);
            $scope.current_sheet_num = $scope.current_sheet + 1;
        }
    }, false);

    $scope.$watch('current_image_num', function(newPage, oldPage) {
        if (newPage != oldPage) {
            $scope.current_image = $scope.current_image_num - 1;
        }
    }, false);

    $scope.$watch('current_image', function(newPage, oldPage) {
        if (newPage != oldPage) {
            if (typeof $scope.sheets[$scope.current_sheet]['images'] !== "undefined") {
                if ($scope.current_image >= $scope.sheets[$scope.current_sheet]['images'].length)
                    $scope.current_image = $scope.sheets[$scope.current_sheet]['images'].length - 1;
                if ($scope.current_image < 0)
                    $scope.current_image = 0;
            }

            $scope.current_image_num = $scope.current_image + 1;
        }
    }, false);

    $scope.$watch('zoom_step', function(new_val, old_val) {
        $scope.zoom = Math.pow(1.2, $scope.zoom_step);
    }, false);


    $scope.submitSheet = function(sheet_number) {
        if (typeof $scope.sheets[sheet_number] === 'undefined')
            return;

        /* Not dirty? */
        if (!$scope.sheets[sheet_number]['$dirty'])
            return;

        var submitData = $scope.sheets[sheet_number]['data'];

        $scope.sheets[sheet_number]['$dirty'] = false;

        $http.post($scope.sheet_base + sheet_number + '/', { 'data' : submitData })
            .error(function(data, status, headers, config) {
                alert("There was a data loss! The server responded with an error while submitting the data!");
            });
    }

    $scope.delayedSubmitSheet = _.throttle($scope.submitSheet, 2000, {leading: false});

    $scope.last_watch_sheet = $scope.current_sheet;
    $scope.$watch('sheets[current_sheet]', function(newSheet, oldSheet) {
        if ($scope.last_watch_sheet != $scope.current_sheet) {
            /* The expression changed because we switche sheets, ignore the
             * change. */
            $scope.last_watch_sheet = $scope.current_sheet;
            return;
        }

        /* There was no real change if the oldSheet was just the placeholder. */
        if (oldSheet['$loading'])
            return;

        /* Mark the current sheet as diry. */
        $scope.sheets[$scope.current_sheet]['$dirty'] = true;
        /* And trigger delayed submission. */
        $scope.delayedSubmitSheet($scope.current_sheet);
    }, true);



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

    $scope.zoomOut = function() {
        $scope.zoom_step -= 1;
    }

    $scope.zoomIn = function() {
        $scope.zoom_step += 1;
    }

    $(document).keydown(function(event){
        var keyCode = {
          BACKSPACE: 8,
          CAPS_LOCK: 20,
          COMMA: 188,
          CONTROL: 17,
          DELETE: 46,
          DOWN: 40,
          END: 35,
          ENTER: 13,
          ESCAPE: 27,
          HOME: 36,
          INSERT: 45,
          LEFT: 37,
          NUMPAD_ADD: 107,
          NUMPAD_DECIMAL: 110,
          NUMPAD_DIVIDE: 111,
          NUMPAD_ENTER: 108,
          NUMPAD_MULTIPLY: 106,
          NUMPAD_SUBTRACT: 109,
          PAGE_DOWN: 34,
          PAGE_UP: 33,
          PERIOD: 190,
          RIGHT: 39,
          SHIFT: 16,
          SPACE: 32,
          TAB: 9,
          UP: 38  };

        var key = event.keyCode || event.which;

        if (typeof event.target.type === 'undefined') {
            if (key == keyCode.ENTER) {
                if (event.shiftKey) {
                    $scope.prev();
                } else {
                    $scope.next();
                }
                /* We have to $apply manually, as this is done using jQuery. */
                $scope.$apply();
            }
        }
    });

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


