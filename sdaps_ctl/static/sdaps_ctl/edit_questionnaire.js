

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

    url: function() {
      return QEditor.base_url + '/answers/' + this.get('id') + '/';
    },
  });

  var AnswerCollection = QEditor.AnswerCollection = Backbone.Collection.extend({
    model: Answer,

    initialize: function() {
      this.url = QEditor.base_url + '/answers';
    },
  });

  /************************
   * QObjects
   ************************/

  var QObject = QEditor.QObject = Backbone.RelationalModel.extend({

    subModelTypeAttribute: 'qtype',
    subModelTypes: {
      'qhead': 'QEditor.QHead',
      'qmark': 'QEditor.QMark',
      'qmarkgroup': 'QEditor.QMarkGroup',
      'qmarkline': 'QEditor.QMarkLine',
    },

    relations: [{
      type: Backbone.HasMany,
      key: 'answers',
      relatedModel: "QEditor.Answer",
      collectionType: "QEditor.AnswerCollection",
      includeInJSON: 'id',
      reverseRelation: {
        key: 'qobject',
        includeInJSON: 'id',
      },
    }, {
      type: Backbone.HasMany,
      key: 'children',
      relatedModel: "QEditor.QObject",
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
        qtype: 'invalid',
        order: this.nextOrder(),
      };
    },

    nextOrder: function() {
      if (this.collection != undefined)
        return this.collection.nextOrder();
      else
        return 1;
    },

    local_init: function() {
    },

    url: function() {
      return QEditor.base_url + '/qobjects/' + this.get('id') + '/';
    },
  });

  var QHead = QEditor.QHead = QObject.extend({
    defaults: function() {
      return _.extend(this.constructor.__super__.defaults(), {
        qtype: 'qhead',
      });
    },
   });

  var QMark = QEditor.QMark = QObject.extend({
    defaults: function() {
      return _.extend(this.constructor.__super__.defaults(), {
        qtype: 'qmark',
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
        qtype: 'qmarkgroup',
      });
    },
   });

  var QMarkLine = QEditor.QMarkLine = QObject.extend({
    defaults: function() {
      return _.extend(this.constructor.__super__.defaults(), {
        qtype: 'qmarkline',
      });
    },

    local_init: function() {
      new Answer({text: 'lower', qobject: this});
      new Answer({text: 'upper', qobject: this});
    },
   });

  /* The collection of the questions is a questionnaire. */
  var QObjectCollection = QEditor.QObjectCollection = Backbone.Collection.extend({

    initialize: function() {
      this.url = QEditor.base_url + '/qobjects/';
      console.log(this.url);
    },

    model: function(attrs) {
      _.extend(attrs, {collection: this});
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

  });

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
      this.listenTo(this.model, 'change', this.render);

      this.listenTo(this.model, 'add:answers', this.renderFromTemplate);
      this.listenTo(this.model, 'remove:answers', this.renderFromTemplate);
    },

    templateData: function() {
      return this.model.toJSON();
    },

    renderFromTemplate: function() {
      template = _.template($('#'+this.model.attributes.qtype+'-template').html());

      /* See comment for "relations" attribute. */
      this.$el.html(template(this.templateData()));

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

  var QMarkMixin = {
    updateData: function() {
      if (this.model.get('answers').length == 2) {
        this.model.get('answers').models[0].save({text : this.$('.answer0_text').val()});
        this.model.get('answers').models[1].save({text : this.$('.answer1_text').val()});
      }
    },

    templateData: function() {
      data = this.model.toJSON();
      answer_text = this.model.get('answers').pluck('text');
      data['answers'] = answer_text;

      return data;
    },

    render: function() {
      if (this.model.get('answers').length == 2) {
        if ('text' in this.model.get('answers').models[0].changed)
          this.$('.answer0_text').val(this.model.get('answers').models[0].get('text'));
        if ('text' in this.model.get('answers').models[1].changed)
          this.$('.answer1_text').val(this.model.get('answers').models[1].get('text'));
      }

      return this;
    },
  };

  var QMarkView = QObjectView.extend({
    mixins: [QMarkMixin],
  });

  /* Mixin to handle multiple subquestions.
   * It assumes that there is a list element that subitems can be
   * placed into. */
  var MultiQObjectMixin = {
    initialize: function() {
      console.log("initializing mixin!");

      this.listenTo(this.model, 'add:children', this.addChild);
      this.listenTo(this.model, 'remove:children', this.removeChild);

      this.addAllChildren();
    },

    renderFromTemplate: function(qobject) {
      /* Readd children if the template has been rerendered. */
      this.addAllChildren();
    },

    addChild: function(qobject) {
      /* Figure out the class to use.
       * This is either the generic QObject, or one of the subclasses. */

      console.log("adding child!");

      if (qobject.attributes.qtype in QObjectViewLookup)
        var view = new QObjectViewLookup[qobject.attributes.qtype]({model: qobject});
      else
        var view = new QObjectView({model: qobject});

      console.log(this.$('.children')[0]);

      this.$('.children').append(view.render().el);
    },

    addAllChildren: function() {
      this.model.get('children').each(this.addChild, this);
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
    mixins: [QMarkMixin],
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
    /* No events yet! Oh, how boring ... */
    events: {
    },

    initialize: function(element, url) {
      this.setElement(element);

      /* XXX: Hack, this means that we cannot load multiple editors on one page! */
      QEditor.base_url = url;

      this.qobjects = new QObjectCollection; //([], {url: url + '/qobjects'});
      this.answers = new AnswerCollection; //([], {url: url + '/answers'});

      this.listenTo(this.qobjects, 'add', this.addQObject);
      this.listenTo(this.qobjects, 'reset', this.addAll);

      this.qobjects.fetch();
      this.answers.fetch();
    },

    addQObject: function(qobject) {
      /* XXX: Only add questions directly if they do not have a parent. */
      if (qobject.get('parent') !== null)
        return;

      /* Figure out the class to use.
       * This is either the generic QObject, or one of the subclasses. */
      if (qobject.attributes.qtype in QObjectViewLookup)
        var view = new QObjectViewLookup[qobject.attributes.qtype]({model: qobject});
      else
        var view = new QObjectView({model: qobject});

      this.$('.qobjectlist').append(view.render().el);
    },

    addAll: function() {
      this.qobjects.each(this.addQObject, this);
    }
  });

//  var myeditor = new Editor;

//  Questionnaire.create({type : 'qhead'});
//  test = Questionnaire.create({type : 'qmark', text: 'test'});
//  test.local_init();

//  test = Questionnaire.create({type : 'qmark', text: 'test2'});
//  test.local_init();

//  new Answer({text: 'blub', qobject: test});

//  console.log(JSON.stringify(test.get('answers')));

//  test = Questionnaire.create({type : 'qmarkgroup', text: 'markgroup'});
//  test.local_init();

//  child1 = new QMarkLine({text: 'markline 1', parent: test});
//  child2 = new QMarkLine({text: 'markline 2', parent: test});

//  console.log(JSON.stringify(test.get('children')));

}).bind(this));

