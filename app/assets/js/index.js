var fileUpload = document.getElementById("file-upload");
var filesUploaded = document.getElementById("file-upload-filename");

if (fileUpload && fileUpload.addEventListener) {
  fileUpload.addEventListener("change", showFileName);
}

window.onload = function() {
  
  var genericFormErrors = document.getElementById("target_generic-form-errors");
  if(genericFormErrors){
    genericFormErrors.scrollIntoView();
  }

  var textAreas = document.querySelectorAll('textarea');
  for (var i = 0; i < textAreas.length; i++) {
    (function() {
      var area = textAreas[i];
      autoGrow(area);
      area.addEventListener('keyup', function() { autoGrow(area);});
    }());
  }

  positionFooter();
  
};

window.onorientationchange = function() {
  positionFooter();
}

window.onscroll = function() {checkOffset()};

function checkOffset() {

  if(document.getElementById('stickyButtons')) {
    var scrollHeight = document.documentElement.scrollHeight;
    var windowHeight = "innerHeight" in window ? window.innerHeight : document.documentElement.offsetHeight;
    var footer = document.getElementById('pageFooter');

    if(scrollHeight - windowHeight - window.pageYOffset - footer.offsetHeight - 80 <= 0) {
      document.body.classList.add("footer")
    }else {
      document.body.classList.remove("footer")
    }
  }
}

function positionFooter() {
  var footer = document.getElementById('pageFooter');
  var windowHeight = "innerHeight" in window ? window.innerHeight : document.documentElement.offsetHeight;
  var offsetY = windowHeight - footer.offsetTop - footer.offsetHeight;
  footer.style.visibility = "visible";
  
  if(offsetY > 0){
    var currentPaddingTop = parseInt(window.getComputedStyle(footer, null).getPropertyValue('padding-top'))
    footer.style.marginTop = offsetY + currentPaddingTop + "px";
  }
}

function showFileName(event) {
  var input = event.srcElement;
  var fileName = input.files[0].name;
  filesUploaded.innerHTML = "Geselecteerd bestand: <i>" + fileName + "</i>";
}

function autoGrow (oField) {
  if (oField.scrollHeight > oField.clientHeight) {
    oField.style.height = oField.scrollHeight + "px";
  }
}

if (document.addEventListener) {
  document.addEventListener(
    "invalid",
    function (e) {
      e.target.className += " invalid";
    },
    true
  );
}

function sortOnData(items, key) {
  items.sort(function (a, b) {
    if (a.dataset[key] < b.dataset[key]) {
      return -1;
    } else if (a.dataset[key] > b.dataset[key]) {
      return 1;
    }
    return 0;
  });
}

!(function (w, d) {
  var handlers = {
    'modal': function (e) {
      
      e.preventDefault();
      var el =
          (this.hash && document.getElementById(this.hash.substring(1))) ||
          (this.dataset.contentid &&
            document.getElementById(this.dataset.contentid)),
        url = this.href,
        rootElem =
          (this.dataset.root && document.querySelector(this.dataset.root)) ||
          document.body,
        template =
          '<div class="modal-inner">[[CONTENT]]</div><a href="#" class="modal-close--bg" data-handler="modal-close"></a>';
      var content = false;

      var _render = function (content) {
        var modal = document.createElement("div");
        modal.classList.add("modal");
        modal.innerHTML = template.replace("[[CONTENT]]", content);
        rootElem.appendChild(modal);
        
        var iframe = modal.querySelector('iframe');
        if(iframe !== null) {
          iframe.setAttribute('src', iframe.dataset.src);
          iframe.onload = function() {
            modal.classList.add("active");
            var doc = iframe.contentDocument? iframe.contentDocument: iframe.contentWindow.document;
            var innerElement = doc.querySelector(".site-container");
            var yPos = (window.innerHeight - innerElement.offsetHeight)/2;
            doc.querySelector("body").classList.add('isInIframe');
            iframe.style.height = innerElement.offsetHeight + 20 + "px";
            modal.querySelector('.modal-inner').style.top = yPos > 0 ? yPos : 0 +"px";
          }
        }else{
          setTimeout(function () {
            modal.classList.add("active");
          }, 300);
        }
      };

      if (el) {
        content = el.innerHTML;
        _render(content);
      } else if (url) {
        helpers.ajax(url, function (response) {
          if (response.status >= 200 && response.status < 400) {
            var r = document.createElement("div");
            r.innerHTML = response.responseText;

            (content = r.querySelector("main")) && _render(content.innerHTML);
          } else {
            w.location = url;
          }
        });
      } else {
        w.location = url;
      }
      document.body.classList.add("modal-active");
    },
    "modal-close": function (e) {
      var modal = parent.document.querySelector('.modal.active');
      parent.document.body.classList.remove("modal-active");
      document.body.classList.remove("modal-active");
      if (modal) {
        this.handled = true;
        modal.parentNode.removeChild(modal);
      }
    },
    "show-loading": function (e) {
      document.body.classList.add("show-loading");
    },
    "form-approve": function (e) {
      var prompt = parent.document.querySelector('[data-handler="prompt-approve"]');
      prompt.classList.remove("show-prompt-disapprove");
      prompt.classList.remove("show-prompt-pending");
      prompt.classList.add("show-prompt-approve");
    },
    "form-disapprove": function (e) {
      var prompt = parent.document.querySelector('[data-handler="prompt-approve"]');
      prompt.classList.remove("show-prompt-approve");
      prompt.classList.remove("show-prompt-pending");
      prompt.classList.add("show-prompt-disapprove");
    },
    "form-pending": function (e) {
      var prompt = parent.document.querySelector('[data-handler="prompt-approve"]');
      prompt.classList.remove("show-prompt-approve");
      prompt.classList.remove("show-prompt-disapprove");
      prompt.classList.add("show-prompt-pending");
    },
    "form-approve-cancel": function (e) {
      var prompt = parent.document.querySelector('[data-handler="prompt-approve"]');
      prompt.classList.remove("show-prompt-approve");
      prompt.classList.remove("show-prompt-disapprove");
      prompt.classList.remove("show-prompt-pending");
    },
    "print-page": function(e) {
      window.print();
    },
    "copy-to-input": function(e) {
      var clickedElement = _closest(e.target, '[data-handler="copy-to-input"]')
      var targetInput = document.getElementById("id_"+clickedElement.dataset.targetinput);
      var copiedText = clickedElement.previousElementSibling.textContent;
      targetInput.value = copiedText;
    
    },    
    "close-details": function (e) {
      var self = _closest(e.target, '[data-handler="close-details"]'),
        //moment = _closest(self, "[data-m"),
        details = _closest(self, "details");
        details.open = false;
    },
    "moment-up": function (e) {
      e.preventDefault();
      var moment = _closest(e.target, "[data-moment]");
      _closest(e.target, "[data-edit-timeline]").order(-1, moment);
    },
    "moment-down": function (e) {
      e.preventDefault();
      var moment = _closest(e.target, "[data-moment]");
      _closest(e.target, "[data-edit-timeline]").order(1, moment);
    },
    "new-moment": function (e) {
      e.preventDefault();
      var self = _closest(e.target, '[data-handler="new-moment"]');
      var moment = _closest(e.target, "[data-id]"),
        momentListContainer = moment.parentNode,
        proto = d.querySelector("[data-moment-proto]").cloneNode(true);
      _insertAfter(proto, moment);
      momentListContainer.classList.add("details-list-wrapper--edit");
      self.style.display = "none";
      proto.style.display = "block";
      proto.dataset.decorator = "edit-moment";
      proto.querySelector("input").focus();
      _decorate();
    },
    "exit-new-moment": function (e) {
      e.preventDefault();
      var self = _closest(e.target, '[data-handler="exit-new-moment"]'),
        moment = _closest(self, "[data-moment]"),
        prevMoment = moment.previousSibling,
        momentListContainer = moment.parentNode,
        new_moment_button = moment.previousSibling.querySelector(
          '[data-handler="new-moment"]'
        );
      prevMoment.querySelector('[data-handler="new-moment"]').style.display =
        "block";
      moment.parentElement.removeChild(moment);
      momentListContainer.classList.remove("details-list-wrapper--edit");
    },
    "delete-moment": function (e) {
      e.preventDefault();
      var self = _closest(e.target, '[data-handler="delete-moment"]'),
        container = _closest(self, "[data-edit-moment]");

      if (
        confirm(
          "Weet u zeker dat u het timeline item met naam '" +
            container.querySelector('[name$="name"]').value +
            "' wilt verwijderen"
        )
      ) {
        if (!container.dataset.id) {
          container.parentNode.removeChild(container);
        } else {
          container.delete();
        }
      }
    },
    "exit-edit-moment": function (e) {
      e.preventDefault();
      var self = _closest(e.target, '[data-handler="exit-edit-moment"]'),
        momentListContainer = _closest(self, ".details-list-wrapper"),
        moments = momentListContainer.querySelectorAll("[data-moment]");
      momentListContainer.classList.remove("details-list-wrapper--edit");

      for (var i = 0; i < moments.length; i++) {
        moments[i].classList.remove("details-wrapper--edit");
      }
    },
    "enter-edit-moment": function (e) {
      e.preventDefault();
      var self = _closest(e.target, '[data-handler="enter-edit-moment"]'),
        moment = _closest(e.target, "[data-moment]"),
        momentListContainer = moment.parentNode;
      momentListContainer.classList.add("details-list-wrapper--edit");
      moment.classList.add("details-wrapper--edit");
      moment.querySelector("input").focus();
    },
    "open-moment": function (e) {
      var self = _closest(e.target, '[data-handler="open-moment"]'),
        moment = _closest(self, "[data-moment]"),
        details = moment.querySelector("details"),
        momentListContainer = moment.parentNode,
        buttons = momentListContainer.querySelectorAll(
          ".change-order button, .new-moment__add"
        );
      //momentListContainer.classList[details.hasAttribute('open') ? 'remove' : 'add']('edit-mode');
      if (
        momentListContainer.classList.contains("details-list-wrapper--edit")
      ) {
        e.preventDefault();
      }
    },
    "save-moment": function (e) {
      e.preventDefault();
      var self = _closest(e.target, '[data-handler="save-moment"]'),
        moment = _closest(self, "[data-moment]"),
        exitEditElem = moment.querySelector(
          '[data-handler="exit-edit-moment"]'
        );
      moment.submit(function () {
        exitEditElem.click();
      });
    },
    "ajax-forms-submit": function (e) {
      e.preventDefault();
      var form = _closest(this, "form"),
        selector = ".site-container",
        savingAlertTmpl = '<p class="alert__message">Bezig met opslaan...</p>',
        _getData = function () {
          var data = new FormData(form);
          return data;
        },
        _submit = function (e) {
          e && e.preventDefault();
          var alertLi = document.createElement("li"),
            alertContainer = document.querySelector(".alert-container");
          alertContainer.innerHTML = "";
          alertLi.setAttribute("id", "busy_alert");
          alertLi.classList.add("alert");
          alertLi.classList.add("alert--busy");
          alertLi.innerHTML = savingAlertTmpl;
          alertContainer.appendChild(alertLi);
          helpers.ajax({
            type: "POST",
            url: ".",
            data: _getData(),
            callback: function (responseText) {
              var div = document.createElement("div");
              div.innerHTML = responseText;
              var result = div.querySelectorAll(selector),
                target = d.querySelectorAll(selector);
              if (result && target) {
                for (var i = 0; i < target.length; i++) {
                  target[i].innerHTML = result[i].innerHTML;

                  // IE11 placeholder bug FIX
                  var els = target[i].querySelectorAll("[placeholder]");
                  for (var l = 0; l < els.length; l++) {
                    if (els[l].getAttribute("placeholder") === els[l].value)
                      els[l].value = "";
                  }
                }
              }
              _decorate();
            },
            errors: function (responseText) {
              console.log(responseText);
            },
          });
        };
      helpers.debounce(_submit, 1000, "ajax-forms-submit");
    },

    void: function (e) {
      e.preventDefault();
    },
  };
  var decorators = {
    "select-form-option": function () {
      var self = this,
        urlParams = new URLSearchParams(window.location.search),
        formConfigSlug=urlParams.get('form_config_slug'),
        input = d.querySelector('input[value="'+formConfigSlug+'"]'),
        _init = function(){
          if (input){
            input.checked = true;
          }
        };
      _init();
    },
    "form-rule": function () {
      var self = this,
        ruleData = JSON.parse(self.dataset.ruleData),
        fields = self.querySelectorAll('input[type="radio"]'),
        _getValue = function() {
          if (self.querySelector('input[type="radio"]:checked')){
            return self.querySelector('input[type="radio"]:checked').value;
          }
          return null;
        }
        _change = function(e){
          e && e.preventDefault();
          var i = 0,
            j = 0,
            v = parseInt(_getValue(), 10);
          for (i = 0; i < ruleData.length; i++){
            var show = ruleData[i].values.includes(v);
            for (j = 0; j < ruleData[i].fields.length; j++){
              var f = document.querySelector('[name="'+ruleData[i].fields[j]+'"]'),
                  s = document.querySelector('.section#'+ruleData[i].fields[j]),
                  sn = document.querySelector('#section_nav_'+ruleData[i].fields[j]);
              if (f) {
                var c = _closest(f, '.form-field-history-container');
                c.classList[show?'remove':'add']('hide-animated');
                c.classList[show?'add':'remove']('show-animated');
                
              }else if (s){
                s.classList[show?'remove':'add']('hide-animated');
                s.classList[show?'add':'remove']('show-animated');
              }
              if (sn) {
                sn.classList[show?'remove':'add']('hide');
              }
            }
          }
        },
        _init = function(){};
      _change();
      Array.prototype.forEach.call(fields, function(radio) {
        radio.addEventListener('change', _change);
     });
    },
    "document-name-exists": function () {
      var self = this,
        input = self.querySelector('input[name$="name"]'),
        wrapper = _closest(input, ".form-field"),
        errorMessageTmpl =
          'Er bestaat al een document met deze naam. Wilt u een nieuwe versie van dit document uploaden? <a href="[[link]]">Klik hier <span class="sr-only">om een nieuwe versie te uploaden</span></a>.',
        id = self.dataset.documentId,
        q = "",
        _init = function () {
          wrapper.style.cssText = "position: relative";
        },
        _getData = function () {
          var data = { name: q };
          if (id) {
            data.id = id;
          }
          return data;
        },
        _search = function () {
          var errorMessageElem = wrapper.querySelector(".error-text");
          input.setCustomValidity("");
          if (errorMessageElem) {
            wrapper.removeChild(wrapper.querySelector(".error-text"));
          }
          helpers.ajax({
            type: "POST",
            url: "/document/naam-bestaat",
            data: JSON.stringify(_getData()),
            headers: {
              "X-Requested-With": "XMLHttpRequest",
              "Content-Type": "application/x-www-form-urlencoded",
              "X-CSRFToken": d.querySelector(
                'input[name="csrfmiddlewaretoken"]'
              ).value,
            },
            callback: function (responseText) {
              var response = JSON.parse(responseText);
              if (response.message) {
                input.setCustomValidity("invalid");
                var span = document.createElement("p");
                span.classList.add("error-text");
                span.innerHTML = errorMessageTmpl
                  .trim()
                  .replace("[[link]]", response.message);
                _insertAfter(span, input);
              }
            },
          });
        },
        _keyUp = function (e) {
          if (e.keyCode === 38 || e.keyCode === 40) {
            e.preventDefault();
          } else {
            q = input.value.trim();
            _search();
          }
        };
      input.addEventListener("blur", _keyUp);
      _init();
    },
    "edit-moment": function () {
      var saveStateTimeout;
      var self = this,
        id = this.dataset.id,
        _getFormData = function () {
          var data = {},
            i,
            fields = self.querySelectorAll(
              'input[type="text"], input[type="hidden"], textarea'
            ),
            organizationFields = self.querySelectorAll(
              'input[name$="organizations"]:checked'
            );
          for (i = 0; i < fields.length; i++) {
            var nameSplit = fields[i].getAttribute("name").split("-");
            data[nameSplit[nameSplit.length - 1]] = fields[i].value;
          }
          data["organizations"] = [];
          for (i = 0; i < organizationFields.length; i++) {
            data["organizations"].push(organizationFields[i].value);
          }
          if (self.dataset.id) {
            data["id"] = self.dataset.id;
          }
          return data;
        },
        _updateView = function (data) {
          var i, j;
          for (var k in data) {
            if (data.hasOwnProperty(k)) {
              var elem = self.querySelectorAll("[data-moment-" + k + "]");

              for (i = 0; i < elem.length; i++) {
                if (data[k].value instanceof Array) {
                  var ul = elem[i].querySelector("ul"),
                    items = ul.querySelectorAll("li");
                  for (j = 0; j < items.length; j++) {
                    items[j].style.cssText = "display: none";
                  }
                  if (!data[k].value.length) {
                    items[items.length - 1].style.cssText = "display: initial";
                  } else {
                    for (j = 0; j < data[k].value.length; j++) {
                      ul.querySelector(
                        '[data-listitem-id="' + data[k].value[j] + '"]'
                      ).style.cssText = "display: initial";
                    }
                  }
                } else {
                  elem[i].innerHTML = data[k].value.replace(
                    /(?:\r\n|\r|\n)/g,
                    "<br>"
                  );
                }
              }
            }
          }
        },
        _clearErrorMessages = function () {
          var elems = self.querySelectorAll("[data-error-message]");
          for (var i = 0; i < elems.length; i++) {
            delete elems[i].dataset.errorMessage;
          }
        },
        _init = function () {
          var isNewElement = self.classList.contains(
              "details-wrapper--new-moment"
            ),
            firstElement = self.querySelector('input[name$="name"]'),
            lastElement = isNewElement
              ? self.querySelector('button[data-handler="exit-new-moment"]')
              : self.querySelector('button[data-handler="exit-edit-moment"]'),
            enableElements = self.querySelectorAll('[disabled="disabled"]'),
            addEditmode = self.querySelectorAll(".data-edit-mode"),
            deleteElements = self.querySelectorAll("[data-js-delete]"),
            details = self.querySelector("details"),
            i;

          lastElement.addEventListener("keydown", function (e) {
            if (e.keyCode === 9) {
              firstElement.focus();
              e.preventDefault();
            }
          });
          if (!self.classList.contains("details-wrapper--new-moment")) {
            self.classList.remove("edit-mode");
            details.removeAttribute("open");
          }

          if (details) {
          }
          for (i = 0; i < deleteElements.length; i++) {
            deleteElements[i].parentNode.removeChild(deleteElements[i]);
          }
          for (i = 0; i < enableElements.length; i++) {
            enableElements[i].removeAttribute("disabled");
          }
          for (i = 0; i < addEditmode.length; i++) {
            addEditmode[i].dataset.editMode = "";
          }
        },
        _delete = function () {
          helpers.ajax({
            type: "POST",
            url: "/timeline/delete-moment",
            data: JSON.stringify({ id: self.dataset.id }),
            headers: {
              "X-Requested-With": "XMLHttpRequest",
              "Content-Type": "application/x-www-form-urlencoded",
              "X-CSRFToken": d.querySelector(
                'input[name="csrfmiddlewaretoken"]'
              ).value,
            },
            callback: function () {
              if (this.status === 200) {
                self.parentNode.removeChild(self);
                d.querySelector("[data-edit-timeline]").save();
              }
            },
          });
        },
        _submit = function (_callback) {
          var data = _getFormData();
          self.classList.add("moment--saving");
          clearTimeout(saveStateTimeout);
          helpers.ajax({
            type: "POST",
            url: "/timeline/update-moment",
            data: JSON.stringify(data),
            headers: {
              "X-Requested-With": "XMLHttpRequest",
              "Content-Type": "application/x-www-form-urlencoded",
              "X-CSRFToken": d.querySelector(
                'input[name="csrfmiddlewaretoken"]'
              ).value,
            },
            callback: function (responseText) {
              var response = JSON.parse(responseText);
              if (this.status === 201) {
                self.dataset.id = response.message.id.value;
                self.classList.remove("details-wrapper--new-moment");
                delete self.dataset.momentProto;
                d.querySelector("[data-edit-timeline]").save();
              } else {
                self.querySelector(
                  ".alert--saving .alert__message"
                ).textContent = "Uw wijzigingen worden opgeslagen...";
                self.querySelector(
                  ".alert--saved .alert__message"
                ).textContent = "Wijzigingen opgeslagen.";
              }
              if (self.previousSibling.classList) {
                self.previousSibling.querySelector(
                  '[data-handler="new-moment"]'
                ).style.display = "block";
              }
              self.classList.add("moment--saved");
              _updateView(response.message);
              _clearErrorMessages();
              if (_callback && typeof _callback === "function") {
                _callback();
              }
              saveStateTimeout = setTimeout(function () {
                self.classList.remove("moment--saved");
                self.classList.remove("moment--saving");
                self.classList.remove("moment--error");
              }, 2000);
            },
            error: function (responseText) {
              var response = JSON.parse(responseText);
              self.classList.add("moment--error");
              saveStateTimeout = setTimeout(function () {
                self.classList.remove("moment--saved");
                self.classList.remove("moment--saving");
                self.classList.remove("moment--error");
              }, 2000);

              if (this.status === 422) {
                for (var k in response.message) {
                  if (response.message.hasOwnProperty(k)) {
                    self.querySelector(
                      '[name$="' + k + '"]'
                    ).dataset.errorMessage = response.message[k];
                  }
                }
              }
            },
          });
        };
      _init();
      self.dataset.editMoment = self;
      self.submit = _submit;
      self.delete = _delete;
    },
    "edit-timeline": function () {
      var self = this,
        momentContainer = self.querySelector("[data-moment-container]"),
        savedMomentQ = "[data-id]",
        momentQ = "[data-moment]",
        _submit = function (data) {
          helpers.ajax({
            type: "POST",
            url: "/timeline/order",
            headers: {
              "X-Requested-With": "XMLHttpRequest",
              "Content-Type": "application/x-www-form-urlencoded",
              "X-CSRFToken": document.querySelector(
                'input[name="csrfmiddlewaretoken"]'
              ).value,
            },
            data: JSON.stringify(data),
          });
        },
        _save = function () {
          var data = _toArray(
            momentContainer.querySelectorAll(savedMomentQ)
          ).map(function (e, i) {
            return { id: e.dataset.id, order: i };
          });
          _submit(data);
        },
        _order = function (direction, momentElem) {
          var items = _toArray(momentContainer.querySelectorAll(momentQ)),
            index = items.indexOf(momentElem),
            nextElem = items[index + direction];
          if (nextElem) {
            var currentClone = momentElem.cloneNode(true);
            var nextClone = nextElem.cloneNode(true);
            var currentRect = momentElem.getBoundingClientRect();
            var nextRect = nextElem.getBoundingClientRect();
            var parentRect = nextElem.parentNode.getBoundingClientRect();
            nextElem.style.opacity = 0;
            momentElem.style.opacity = 0;
            currentClone.style.position = "absolute";
            currentClone.style.width = momentElem.offsetWidth + "px";
            currentClone.style.height = momentElem.offsetHeight + "px";
            currentClone.style.top = currentRect.top - parentRect.top + "px";
            currentClone.style.transition =
              "all .5s cubic-bezier(0.165, 0.84, 0.44, 1)";
            currentClone.style.zIndex = 1001;

            nextClone.style.position = "absolute";
            nextClone.style.width = momentElem.offsetWidth + "px";
            nextClone.style.height = momentElem.offsetHeight + "px";
            nextClone.style.top = nextRect.top - parentRect.top + "px";
            nextClone.style.transition =
              "all .5s cubic-bezier(0.165, 0.84, 0.44, 1)";
            nextClone.style.zIndex = 1000;

            momentElem.parentNode.appendChild(currentClone);
            momentElem.parentNode.appendChild(nextClone);

            setTimeout(function () {
              currentClone.style.transform =
                "translate(0, " + direction * nextElem.offsetHeight + "px)";
              nextClone.style.transform =
                "translate(0, " + -direction * momentElem.offsetHeight + "px)";
            }, 1);
            setTimeout(function () {
              currentClone.parentNode.removeChild(currentClone);
              nextClone.parentNode.removeChild(nextClone);
              nextElem.style.opacity = 1;
              momentElem.style.opacity = 1;
              if (direction < 0) {
                _insertAfter(nextElem, momentElem);
              } else {
                _insertAfter(momentElem, nextElem);
              }
              _save();
            }, 500);
          }
        },
        _init = function () {
          var deleteElements = document.querySelectorAll(
              "[data-submit-container]"
            ),
            i;
          for (i = 0; i < deleteElements.length; i++) {
            deleteElements[i].parentNode.removeChild(deleteElements[i]);
          }
          if (self.classList.contains("details-wrapper--new-moment")) {
            self.style.display = "none";
          }
        };
      _init();
      self.dataset.editTimeline = self;
      self.order = _order;
      self.save = _save;
    },
    "timeline-sort": function () {
      var self = this,
        momentFormList = self.querySelectorAll("[data-moment]"),
        _init = function (items) {
          var momentContainer = items[0].parentNode;
          var i;
          momentContainer.style.display = "flex";
          momentContainer.style.flexDirection = "column";
          for (i = 0; i < items.length; i++) {
            items[i].dataset.order = i;
            items[i].style.order = i;
          }
        },
        _moveMoment = function (direction, momentElem) {
          var items = Array.prototype.slice.call(
            momentElem.parentNode.children
          );
          sortOnData(items, "order");
          var index = items.indexOf(momentElem),
            currentOrder = momentElem.dataset.order,
            nextElem = items[index + direction];
          if (nextElem) {
            momentElem.dataset.order = nextElem.dataset.order;
            nextElem.dataset.order = currentOrder;
            momentElem.style.order = momentElem.dataset.order;
            nextElem.style.order = nextElem.dataset.order;
          }
        },
        _submit = function () {
          for (var i = 0; i < momentFormList.length; i++) {
            if (!momentFormList[i].hasAttribute("data-new-moment")) {
              momentFormList[i].querySelector('input[name$="-order"]').value =
                momentFormList[i].dataset.order;
            }
          }
        };

      _init(momentFormList);
      this.moveMoment = _moveMoment;
      this.addEventListener("submit", _submit);
    },
  };

  d.addEventListener("click", function (t) {
    var k,
      e,
      a = t && t.target;
    if ((a = _closest(a, "[data-handler]"))) {
      var r = a.getAttribute("data-handler").split(/\s+/);
      if (
        "A" == a.tagName &&
        (t.metaKey || t.shiftKey || t.ctrlKey || t.altKey)
      )
        return;
      for (e = 0; e < r.length; e++) {
        k = r[e].split(/[\(\)]/);
        handlers[k[0]] && handlers[k[0]].call(a, t, k[1]);
      }
    }
  });
  var _decorate = function () {
    var k,
      i,
      j,
      decoratorString,
      el,
      els = d.querySelectorAll("[data-decorator]");
    for (i = 0; i < els.length; i++) {
      for (
        decoratorString = (el = els[i])
          .getAttribute("data-decorator")
          .split(/\s+/),
          j = 0;
        j < decoratorString.length;
        j++
      ) {
        k = decoratorString[j].split(/[\(\)]/);
        decorators[k[0]] && decorators[k[0]].call(el, k[1]);
        el.removeAttribute("data-decorator");
      }
    }
  };
  var _closest = function (e, t) {
    var ms = "MatchesSelector",
      c;
    ["matches", "webkit" + ms, "moz" + ms, "ms" + ms, "o" + ms].some(function (
      e
    ) {
      return "function" == typeof document.body[e] && ((c = e), !0);
    });
    var r = e;
    try {
      for (; e; ) {
        if (r && r[c](t)) return r;
        e = r = e.parentElement;
      }
    } catch (e) {}
    return null;
  };

  var _formDataToQueryString = function (data) {
    var out = "",
      i;
    for (var k in data) {
      if (data.hasOwnProperty(k)) {
        out += encodeURIComponent(k) + "=" + encodeURIComponent(data[k]) + "&";
      }
    }
    return out;
  };
  var _toArray = function (a) {
    return Array.prototype.slice.call(a);
  };
  var _insertAfter = function (newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
  };
  var helpers = {
    ajax: function (options) {
      var request = new XMLHttpRequest(),
        defaultHeaders = {
          // 'X-Requested-With': 'XMLHttpRequest',
          // 'Content-Type': 'application/x-www-form-urlencoded',
          // 'X-CSRFToken': d.querySelector('input[name="csrfmiddlewaretoken"]').value
        },
        headers = helpers.merge_options(options.headers || {}, defaultHeaders);
      request.open(options.type || "GET", options.url, true);
      for (var k in headers) {
        if (headers.hasOwnProperty(k)) {
          request.setRequestHeader(k, headers[k]);
        }
      }
      request.onreadystatechange = function () {
        if (request.readyState === XMLHttpRequest.DONE) {
          if (request.status >= 200 && request.status < 400) {
            if (options.callback && typeof options.callback === "function") {
              options.callback.call(request, request.responseText);
            }
          } else if (request.status === 400) {
            alert("Er ging iets mis.");
          } else {
            if (options.error && typeof options.error === "function") {
              options.error.call(request, request.responseText);
            }
          }
        }
      };
      request.send(options.data);
      return request;
    },
    debounce: function (callback, delay, timeoutKey) {
      var lastClick = helpers.debounceTimeout[timeoutKey] || 0;
      if (lastClick >= Date.now() - delay) return;
      helpers.debounceTimeout[timeoutKey] = Date.now();
      callback();
    },
    debounceTimeout: {},
    serialize: function (form, evt) {
      var evt = evt || window.event;
      evt.target = evt.target || evt.srcElement || null;
      var field,
        query = "";
      if (typeof form === "object" && form.nodeName === "FORM") {
        for (i = form.elements.length - 1; i >= 0; i--) {
          field = form.elements[i];
          if (field.name && field.type !== "file" && field.type !== "reset") {
            if (field.type === "select-multiple") {
              for (j = form.elements[i].options.length - 1; j >= 0; j--) {
                if (field.options[j].selected) {
                  query +=
                    "&" +
                    field.name +
                    "=" +
                    encodeURIComponent(field.options[j].value).replace(
                      /%20/g,
                      "+"
                    );
                }
              }
            } else {
              if (
                (field.type !== "submit" && field.type !== "button") ||
                evt.target === field
              ) {
                if (
                  (field.type !== "checkbox" && field.type !== "radio") ||
                  field.checked
                ) {
                  query +=
                    "&" +
                    field.name +
                    "=" +
                    encodeURIComponent(field.value).replace(/%20/g, "+");
                }
              }
            }
          }
        }
      }
      return query.substr(1);
    },
    merge_options: function (obj1, obj2) {
      var obj3 = {};
      for (var attrname1 in obj1) {
        if (obj1.hasOwnProperty(attrname1)) {
          obj3[attrname1] = obj1[attrname1];
        }
      }
      for (var attrname2 in obj2) {
        if (obj2.hasOwnProperty(attrname2)) {
          obj3[attrname2] = obj2[attrname2];
        }
      }
      return obj3;
    },
  };
  document.querySelector("html").classList.remove("no-js");
  _decorate();
})(window, document.documentElement);
