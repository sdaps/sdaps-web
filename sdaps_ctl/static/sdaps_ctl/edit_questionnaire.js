

/* Load everything (using JQuery) once the document is ready. */

$(function(){

  /************************
   * Answers
   ************************/

  var Answer = Backbone.RelationalModel.extend({
    defaults: function() {
      return {
        text: 'answer',
        btype: 'check',
        columns: 1,
        height: 1.2,
      };
    },

    /* XXX: No syncing for now! */
    sync: function() {
    },
  });

  var AnswerCollection = Backbone.Collection.extend({
    model: Answer,

    /* XXX: No syncing for now! */
    sync: function() {
    },
  });

  var Answers = new AnswerCollection;

  /************************
   * QObjects
   ************************/

  var QObject = Backbone.RelationalModel.extend({

    /* NOTE: We post the answers key to the server, which simply ignores it.
     *       However, that is why using toJSON below works fine for the
     *       templates, as the data is included in the objects. */
    relations: [{
      type: Backbone.HasMany,
      key: 'answers',
      relatedModel: Answer,
      collectionType: AnswerCollection,
      reverseRelation: {
        key: 'qobject',
        includeInJSON: 'id',
      },
    }],

    defaults: function() {
      return {
        text: 'please add a text here',
        type: 'invalid',
        order: Questionnaire.nextOrder(),
      };
    },

    sync: function() {
    },

    local_init: function() {
    },
  });

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
      });
    },

    local_init: function() {
      Answers.create({text: 'lower', qobject: this});
      Answers.create({text: 'upper', qobject: this});
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

    events: {
      "blur .text" : "updateData",
    },

    initialize: function() {
      /* Render once so that objects are created. */
      this.renderFromTemplate();

      /* Re-render any time this object changes. */
      this.listenTo(this.model, 'change', this.sync);

      /* Need a full render! */
      this.listenTo(this.model, 'add:answers', this.renderFromTemplate);
      this.listenTo(this.model, 'remove:answers', this.renderFromTemplate);
    },

    renderFromTemplate: function() {
      template = _.template($('#'+this.model.attributes.type+'-template').html());

      /* See comment for "relations" attribute. */
      this.$el.html(template(this.model.toJSON()));

      return this;
    },

    render: function() {
      if ('text' in this.model.changed)
        this.$('.qobject_text').val(this.model.get('text'));

      return this;
    },

    updateData: function() {
      this.model.save({text : this.$('.qobject_text').val()});
    },

    answerAdded: function(answer) {
      this.listenTo(answer, 'change', this.render);

      this.renderFromTemplate();
    },

    destroy: function() {
      this.model.destroy();
    },

  });

  var QMarkView = QObjectView.extend({
    updateData: function() {
      QMarkView.__super__.updateData.call(this, arguments);

      if (this.model.get('answers').length == 2) {
        this.model.get('answers').models[0].save({text : this.$('.answer0_text').val()});
        this.model.get('answers').models[1].save({text : this.$('.answer1_text').val()});
      }
    },

    render: function() {
      QMarkView.__super__.render.call(this, arguments);

      if (this.model.get('answers').length == 2) {
        if ('text' in this.model.get('answers').models[0].changed)
          this.$('.answer0_text').val(this.model.get('answers').models[0].get('text'));
        if ('text' in this.model.get('answers').models[1].changed)
          this.$('.answer1_text').val(this.model.get('answers').models[1].get('text'));
      }

      return this;
    },
  });

  /* Dictionary of view types. Note that we solved the lookup differently for
   * the model (ie. with a chain of if statements). */
  var QObjectViewTypeLookup = {
    qmark: QMarkView,
  };

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
      /* Figure out the class to use.
       * This is either the generic QObject, or one of the subclasses. */
      if (qobject.attributes.type in QObjectViewTypeLookup)
        var view = new QObjectViewTypeLookup[qobject.attributes.type]({model: qobject});
      else
        var view = new QObjectView({model: qobject});

      this.$('#questionnaire_view').append(view.render().el);
    },

    addAll: function() {
      Questionnaire.each(this.addQObject, this);
    }
  });

  var QEditor = new QuestionnaireView;

  Questionnaire.create({type : 'qhead'});
  test = Questionnaire.create({type : 'qmark', text: 'test'});
  test.local_init();

});

