

/* Load everything (using JQuery) once the document is ready. */

$((function(){

  var root = this;

  var QEditor;
  if (typeof exports !== 'undefined') {
    QEditor = exports;
  } else {
    QEditor = root.QEditor = {};
  }

  /* Patch Backbone with Cocktail so that we can use the "mixins" attribute. */
  Cocktail.patch(Backbone);

  /************************
   * Answers
   ************************/

  var Answer = QEditor.Answer = Backbone.RelationalModel.extend({
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

  var AnswerCollection = QEditor.AnswerCollection = Backbone.Collection.extend({
    model: Answer,

    /* XXX: No syncing for now! */
    sync: function() {
    },
  });

  /************************
   * QObjects
   ************************/

  var QObject = QEditor.QObject = Backbone.RelationalModel.extend({

    subModelTypeAttribute: 'type',
    subModelTypes: {
      'qhead': 'QEditor.QHead',
      'qmark': 'QEditor.QMark',
      'qmarkgroup': 'QEditor.QMarkGroup',
      'qmarkline': 'QEditor.QMarkLine',
    },

    /* NOTE: We post the answers key to the server, which simply ignores it.
     *       However, that is why using toJSON below works fine for the
     *       templates, as the data is included in the objects. */
    relations: [{
      type: Backbone.HasMany,
      key: 'answers',
      relatedModel: "QEditor.Answer",
      collectionType: "QEditor.AnswerCollection",
      reverseRelation: {
        key: 'qobject',
        includeInJSON: 'id',
      },
    }, {
      type: Backbone.HasMany,
      key: 'children',
      relatedModel: "QEditor.QMarkLine",
      collectionType: "QEditor.QObjectCollection",
      includeInJSON: 'id',
      reverseRelation: {
        key: 'parent',
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

  var QHead = QEditor.QHead = QObject.extend({
    defaults: function() {
      return _.extend(this.constructor.__super__.defaults(), {
        type: 'qhead',
      });
    },
   });

  var QMark = QEditor.QMark = QObject.extend({
    defaults: function() {
      return _.extend(this.constructor.__super__.defaults(), {
        type: 'qmark',
      });
    },

    local_init: function() {
      new Answer({text: 'lower', qobject: this});
      new Answer({text: 'upper', qobject: this});
    },
   });

  var QMarkGroup = QEditor.QMarkGroup = QObject.extend({
    defaults: function() {
      return _.extend(this.constructor.__super__.defaults(), {
        type: 'qmarkgroup',
      });
    },
   });

  var QMarkLine = QEditor.QMarkLine = QObject.extend({
    defaults: function() {
      return _.extend(this.constructor.__super__.defaults(), {
        type: 'qmarkline',
      });
    },
   });

  /* The collection of the questions is a questionnaire. */
  var QObjectCollection = QEditor.QObjectCollection = Backbone.Collection.extend({

    model: function(attrs) {
      return QObject.build(attrs);
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
  var Questionnaire = QEditor.Questionnaire = new QObjectCollection;

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

  /* Mixin to handle multiple subquestions.
   * It assumes that there is a list element that subitems can be
   * placed into. */
  var MultiQObjectMixin = {
    initialize: function() {
      this.listenTo(this.model, 'add:children', this.addChild);
      this.listenTo(this.model, 'remove:children', this.removeChild);
    },

    addChild: function(qobject) {
      /* Figure out the class to use.
       * This is either the generic QObject, or one of the subclasses. */
      if (qobject.attributes.type in QObjectViewLookup)
        var view = new QObjectViewLookup[qobject.attributes.type]({model: qobject});
      else
        var view = new QObjectView({model: qobject});

      this.$('.children').append(view.render().el);
    },

    removeChild: function() {
      
    },
  };

  var QMarkGroupView = QObjectView.extend({
    mixins: [MultiQObjectMixin],

    initialize: function() {
      QMarkGroupView.__super__.initialize.call(this, arguments);

    },
  });

  var QMarkLineView = QObjectView.extend({
    initialize: function() {
      QMarkLineView.__super__.initialize.call(this, arguments);
    },
  });

  /* Dictionary of view types. */
  var QObjectViewLookup = {
    qmark: QMarkView,
    qmarkgroup: QMarkGroupView,
    qmarkline: QMarkLineView,
  };

  /************************
   * And the Editor
   ************************/
  var Editor = QEditor.Editor = Backbone.View.extend({
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
      /* Only add questions directly if they do not have a parent. */
      if (qobject.get('parent') !== undefined)
        return;

      /* Figure out the class to use.
       * This is either the generic QObject, or one of the subclasses. */
      if (qobject.attributes.type in QObjectViewLookup)
        var view = new QObjectViewLookup[qobject.attributes.type]({model: qobject});
      else
        var view = new QObjectView({model: qobject});

      this.$('#questionnaire_view').append(view.render().el);
    },

    addAll: function() {
      Questionnaire.each(this.addQObject, this);
    }
  });

  var myeditor = new Editor;

  Questionnaire.create({type : 'qhead'});
  test = Questionnaire.create({type : 'qmark', text: 'test'});
  test.local_init();

  test = Questionnaire.create({type : 'qmark', text: 'test2'});
  test.local_init();

  new Answer({text: 'blub', qobject: test});

  console.log(JSON.stringify(test.get('answers')));

  test = Questionnaire.create({type : 'qmarkgroup', text: 'markgroup'});
  test.local_init();

  child1 = new QMarkLine({text: 'markline 1', parent: test});
  child2 = new QMarkLine({text: 'markline 2', parent: test});

  console.log(JSON.stringify(test.get('children')));

}).bind(this));

