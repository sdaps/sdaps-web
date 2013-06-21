

/* Load everything (using JQuery) once the document is ready. */

$(function(){
  /*
   * Data Model
   */

  var QObject = Backbone.Model.extend({
    defaults: function() {
      return {
        text: 'please add a text here',
        type: 'invalid',
        order: Questionnaire.nextOrder(),
      };
    },

    sync: function() {
    },
  });

  /* Change nothing */
  var QHead = QObject.extend({
    defaults: function() {
      return _.extend(this.constructor.__super__.defaults(), {
        type: 'qhead',
      });
    },
  });

  var QMark = QObject.extend({
    defaults: function() {
      return _.extend(this.constructor.__super__.defaults(), {
        type: 'qmark',
        left_answer: 'left',
        right_answer: 'left',
      });
    },
  });


  /* The collection of the questions is a questionnaire. */
  var QObjects = Backbone.Collection.extend({

    model: function(attrs) {
      if (attrs.type == 'qhead') {
        return new QHead(attrs);
      } else if (attrs.type == 'qmark') {
        return new QMark(attrs);
      } else {
         throw new Error('Unknown qobject type "' + attrs.type + '"!');
      }
    },

    /* TODO: Posting/receiving data! */

    nextOrder: function() {
      if (this.length)
        return this.last().get('order') + 1;
      else
        return 1;
    },

    comparator: 'order',

    /* XXX: No syncing for now! */
    sync: function() {
    },

  });


  /************************
   * Questionnaire
   ************************/
  var Questionnaire = new QObjects;

  /************************
   * Questionnaire View
   ************************/
  var QObjectView = Backbone.View.extend({
    /* Each item is an item in an ordered list, styling handled
     * in the CSS. */
    tagName: 'li',

    /* XXX: Inefficient? */
    render: function() {
      template = _.template($('#'+this.model.attributes.type+'-template').html());

      this.$el.html(template(this.model.toJSON()));

      return this;
    },

    destroy: function() {
      this.model.destroy();
    },
  });


  /************************
   * And the View
   ************************/
  var QuestionnaireView = Backbone.View.extend({
    el: $('#questionnaire_edit'),

    /* No events yet! Oh, how boring ... */
    events: {
    },

    initialize: function() {
      this.listenTo(Questionnaire, 'add', this.addQObject);
      this.listenTo(Questionnaire, 'reset', this.addAll);

      Questionnaire.fetch();
    },

    addQObject: function(qobject) {
      var view = new QObjectView({model: qobject});

      this.$('#questionnaire_view').append(view.render().el);
    },

    addAll: function() {
      Questionnaire.each(this.addQObject, this);
    }
  });

  var QEditor = new QuestionnaireView;

  Questionnaire.create({type : 'qhead', });

});

