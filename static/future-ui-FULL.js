
(function($){
  $.futureUI = function(options) {
    var settings = $.extend({
      message: "Hello Future!",
      type: "card",
      effect: "fade",
      theme: "auto"
    }, options);

    var container = $('#fu-container');
    var element = $('<div class="fu-'+settings.type+' fu-theme-'+settings.theme+'">'+settings.message+'</div>');

    if(settings.effect === "fade"){
      element.hide().appendTo(container).fadeIn(800);
    } else if(settings.effect === "slide"){
      element.hide().appendTo(container).slideDown(800);
    } else if(settings.effect === "typewriter"){
      element.appendTo(container);
      var txt = settings.message, i=0;
      element.text('');
      var typer = setInterval(function(){
        if(i < txt.length){
          element.append(txt.charAt(i));
          i++;
        } else {
          clearInterval(typer);
        }
      }, 50);
    } else {
      element.appendTo(container);
    }
  };

  $.futureUIbutton = function(options){
    var settings = $.extend({
      text: "Click Me",
      onClick: function(){ alert("Button clicked!"); }
    }, options);

    var btn = $('<button class="fu-btn">'+settings.text+'</button>');
    btn.on('click', settings.onClick);
    $('#fu-container').append(btn.hide().fadeIn(500));
  };

  $.futureUIinput = function(options){
    var settings = $.extend({
      label: "Enter text",
      placeholder: "Type here...",
      onChange: function(value){ console.log("Input changed: ", value); }
    }, options);

    var wrapper = $('<div class="fu-input-wrap"></div>');
    var lbl = $('<label class="fu-label">'+settings.label+'</label>');
    var input = $('<input class="fu-input" placeholder="'+settings.placeholder+'">');

    input.on('input', function(){ settings.onChange($(this).val()); });

    wrapper.append(lbl).append(input);
    $('#fu-container').append(wrapper.hide().fadeIn(500));
  };

  $.futureUItoast = function(msg){
    var toast = $('<div class="fu-toast">'+msg+'</div>');
    $('#fu-container').append(toast.hide().fadeIn(400));
    setTimeout(function(){
      toast.fadeOut(400, function(){ $(this).remove(); });
    }, 3000);
  };

  $.futureUIselect = function(options){
    var settings = $.extend({
      label: "Choose",
      items: ["Option 1", "Option 2"],
      onChange: function(val){ console.log(val); }
    }, options);

    var wrap = $('<div class="fu-input-wrap"></div>');
    var lbl = $('<label class="fu-label">'+settings.label+'</label>');
    var sel = $('<select class="fu-input"></select>');

    $.each(settings.items, function(i, item){
      sel.append('<option value="'+item+'">'+item+'</option>');
    });

    sel.on('change', function(){ settings.onChange($(this).val()); });
    wrap.append(lbl).append(sel);
    $('#fu-container').append(wrap.hide().fadeIn(500));
  };

  $.futureUIswitch = function(options){
    var settings = $.extend({
      label: "Toggle",
      onToggle: function(state){ console.log("Toggle state:", state); }
    }, options);

    var wrap = $('<div class="fu-input-wrap"></div>');
    var lbl = $('<label class="fu-label">'+settings.label+'</label>');
    var chk = $('<input type="checkbox" class="fu-switch">');

    chk.on('change', function(){ settings.onToggle($(this).is(':checked')); });
    wrap.append(lbl).append(chk);
    $('#fu-container').append(wrap.hide().fadeIn(500));
  };

  $.futureUIprogress = function(options){
    var settings = $.extend({ value: 0 }, options);
    var bar = $('<div class="fu-progress"><div class="fu-progress-inner"></div></div>');
    $('#fu-container').append(bar.hide().fadeIn(500));
    bar.find('.fu-progress-inner').css('width', settings.value + '%');
    return {
      update: function(val){
        bar.find('.fu-progress-inner').animate({width: val + '%'}, 300);
      }
    };
  };

  $.futureUIbadge = function(text){
    var badge = $('<span class="fu-badge">'+text+'</span>');
    $('#fu-container').append(badge.hide().fadeIn(300));
  };

  $.futureUIglowBadge = function(text){
    var badge = $('<span class="fu-glow-badge">'+text+'</span>');
    $('#fu-container').append(badge.hide().fadeIn(300));
  };

  $.futureUInotifyBell = function(count){
    var bell = $('<div class="fu-bell">🔔 <span class="fu-bell-count">'+count+'</span></div>');
    $('#fu-container').append(bell.hide().fadeIn(300));
  };

  $.futureUIloader = function(){
    var loader = $('<div class="fu-loader"></div>');
    $('#fu-container').append(loader.hide().fadeIn(300));
    return loader;
  };

  $.futureUItabs = function(options){
    var settings = $.extend({
      tabs: [{ title: "Tab 1", content: "Content 1" }]
    }, options);

    var wrap = $('<div class="fu-tabs"></div>');
    var nav = $('<div class="fu-tab-nav"></div>');
    var content = $('<div class="fu-tab-content"></div>');

    $.each(settings.tabs, function(i, tab){
      var btn = $('<button class="fu-btn fu-tab-btn">'+tab.title+'</button>');
      btn.on('click', function(){
        content.html(tab.content);
        nav.find('button').removeClass('active');
        $(this).addClass('active');
      });
      nav.append(btn);
    });

    wrap.append(nav).append(content);
    $('#fu-container').append(wrap.hide().fadeIn(500));
    nav.find('button').first().click();
  };

  $.futureUImodal = function(options){
    var settings = $.extend({
      title: "Modal Title",
      content: "This is a modal window.",
      onClose: function(){},
      autoClose: 2000
    }, options);

    var modal = $(`
      <div class="fu-modal-overlay">
        <div class="fu-modal">
          <div class="fu-modal-header">${settings.title}</div>
          <div class="fu-modal-body">${settings.content}</div>
          <button class="fu-btn fu-modal-close">Close</button>
        </div>
      </div>
    `);

    modal.find('.fu-modal-close').on('click', function(){
      closeModal();
    });

    $('body').append(modal.hide().fadeIn(300));

    if(settings.autoClose && typeof settings.autoClose === "number"){
      setTimeout(closeModal, settings.autoClose);
    }

    function closeModal(){
      modal.fadeOut(300, function(){
        modal.remove();
        settings.onClose();
      });
    }
  };

  $.futureUItooltip = function(selector, text){
    $(selector).each(function(){
      var $el = $(this);
      var tip = $('<span class="fu-tooltip">'+text+'</span>');
      $el.hover(
        function(){
          $('body').append(tip);
          tip.css({
            top: $el.offset().top - $el.outerHeight() - 10,
            left: $el.offset().left,
            position: 'absolute'
          }).fadeIn(200);
        },
        function(){
          tip.fadeOut(200, function(){ tip.remove(); });
        }
      );
    });
  };

  $.futureUIaccordion = function(options){
    var settings = $.extend({
      items: [{ title: "Question?", content: "Answer" }]
    }, options);

    var container = $('<div class="fu-accordion"></div>');
    $.each(settings.items, function(i, item){
      var section = $(`
        <div class="fu-accordion-item">
          <div class="fu-accordion-header">${item.title}</div>
          <div class="fu-accordion-body">${item.content}</div>
        </div>
      `);
      section.find('.fu-accordion-header').on('click', function(){
        section.find('.fu-accordion-body').slideToggle();
        section.siblings().find('.fu-accordion-body').slideUp();
      });
      container.append(section);
    });
    $('#fu-container').append(container.hide().fadeIn(500));
  };

  $.futureUIsnackbar = function(msg){
    var snackbar = $('<div class="fu-snackbar">'+msg+'</div>');
    $('body').append(snackbar.hide().fadeIn(300));
    setTimeout(function(){
      snackbar.fadeOut(300, function(){ $(this).remove(); });
    }, 4000);
  };

  $.futureUIstepper = function(options){
    var settings = $.extend({
      steps: ["Step 1", "Step 2", "Step 3"],
      onStepChange: function(index){ console.log("Step:", index); }
    }, options);

    var wrap = $('<div class="fu-stepper"></div>');
    $.each(settings.steps, function(i, step){
      var btn = $('<div class="fu-step">'+step+'</div>');
      btn.on('click', function(){
        wrap.find('.fu-step').removeClass('active');
        $(this).addClass('active');
        settings.onStepChange(i);
      });
      wrap.append(btn);
    });
    wrap.find('.fu-step').first().addClass('active');
    $('#fu-container').append(wrap.hide().fadeIn(500));
  };

  $.futureUIavatar = function(options){
    var settings = $.extend({
      image: "https://via.placeholder.com/40",
      status: "online"
    }, options);

    var avatar = $(`
      <div class="fu-avatar">
        <img src="${settings.image}" class="fu-avatar-img">
        <span class="fu-status-dot ${settings.status}"></span>
      </div>
    `);
    $('#fu-container').append(avatar.hide().fadeIn(300));
  };

  $.futureUIcountdown = function(seconds){
    var display = $('<div class="fu-countdown"></div>');
    $('#fu-container').append(display.hide().fadeIn(300));

    function updateDisplay(s){
      display.text("⏳ " + s + "s remaining");
    }

    updateDisplay(seconds);
    var interval = setInterval(function(){
      seconds--;
      updateDisplay(seconds);
      if(seconds <= 0){
        clearInterval(interval);
        display.text("✅ Time's up!");
      }
    }, 1000);
  };
})(jQuery);
