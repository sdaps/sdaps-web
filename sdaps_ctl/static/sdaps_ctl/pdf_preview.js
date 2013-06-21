

/* Load everything (using JQuery) once the document is ready. */

(function(){

  var root = this;

  var PDFPreview;
  if (typeof exports !== 'undefined') {
    PDFPreview = exports;
  } else {
    PDFPreview = root.PDFPreview = {};
  }

  var Preview = PDFPreview.Preview = function (element, url) {
    this.el = element;
    this.url = url;
    this.pdf = null;
    this.scale = 0.8;
    this.page = 1;
    this.canvas = this.$('#pdfcanvas')[0];
    this.last_modified_time = null;
    this.timeout_registered = false;

    this._initialize();
  };

  _.extend(Preview.prototype, {
    $: function(selector) {
      return this.el.find(selector);
    },

    _initialize: function() {
      /* Get the drawing context */
      this.ctx = this.canvas.getContext('2d');

      /* Hook up events. */
      this.$('#prev').click(this.prev.bind(this));
      this.$('#next').click(this.next.bind(this));

      /* Start reload loop and do the initial load of the document. */
      this.autoreload();
    },

    prev: function() {
      if (this.page <= 1)
        return;

      this.page--;
      this.render()
    },

    next: function() {
      if (this.page >= this.pdf.numPages)
        return;

      this.page++;
      this.render();
    },

    render: function() {
      preview = this;

      /* Using promise to fetch the page. */
      this.pdf.getPage(this.page).then(function(page) {
        var viewport = page.getViewport(preview.scale);
        preview.canvas.height = viewport.height;
        preview.canvas.width = viewport.width;

        /* Render into the already created context. */
        var renderContext = {
          canvasContext: preview.ctx,
          viewport: viewport
        };
        page.render(renderContext);

        preview.ensureTimeout();
      });

      /* Update the page count*/
      this.$('#page_num')[0].textContent = this.page;
      this.$('#page_count')[0].textContent = this.pdf.numPages;
    },

    download: function() {
      preview = this;

      xhr = new XMLHttpRequest();
      xhr.open("GET", preview.url, true);
      xhr.responseType = "arraybuffer";

      if (preview.last_modified_time !== null) {
          xhr.setRequestHeader('If-Modified-Since', preview.last_modified_time);
      }

      xhr.onload = (function() {
          if (xhr.status == 304) {
            preview.ensureTimeout();
            return;
          }

          if (xhr.status == 404) {
            preview.ensureTimeout();
            return;
          }

          var data = new Uint8Array(xhr.response || xhr.mozResponseArrayBuffer);

          this.last_modified_time = xhr.getResponseHeader('Last-Modified')

          PDFJS.getDocument(data).then(function getPdfHelloWorld(_pdfDoc) {
              preview.pdf = _pdfDoc;
              preview.render();
          });
      }).bind(preview);

      xhr.send(null)
    },

    ensureTimeout: function() {
      if (this.timeout_registered)
        return;

      setTimeout(this.autoreload.bind(preview), 5000);
      this.timeout_registered = true;
    },

    autoreload: function() {
      this.timeout_registered = false;

      this.download();
    },

  });

}).call(this);

