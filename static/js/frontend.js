
function now() {
    return new Date().getTime();
}

function zip() {
    let arrays;
    if (arguments.length === 0)
        return [];

    if (arguments.length === 1)
        if (arguments[0].length === 1 || !Array.isArray(arguments[0]))
            throw "You must pass at least 2 arrays";
        else
            arrays = arguments[0];
    else
        arrays = [...arguments];

    return Array.apply(null,Array(arrays[0].length)).map(function(_,i){
        return arrays.map(function(array){return array[i]})
    });
}

let sidenav_flyout = new class {
    constructor() {
        this.is_any_open = false;
        // this.all_flyouts = $('li.with-flyout');
        this.all_flyouts = new class {
            constructor() {
                this.flyouts = $('li.with-flyout');
                this.collapslibles = this.flyouts.find('.collapsible');
            }
            close() {
                this.flyouts.removeClass('flyout-active');
                this.collapslibles.collapsible('close')
            }
        }();
        this.open_time = 200;
        this.will_close_at = 0;
        this.will_open_at = 0;
        this.next_flyout_to_open = null;
    }
    is_opening_now() {
        return this.is_any_open
                && (this.will_open_at  - this.open_time) < now() && now() < this.will_open_at;
    };
    is_closing_now() {
        return !this.is_any_open
                && (this.will_close_at - this.open_time) < now() && now() < this.will_close_at;
    }
    time_until_open() {
        return this.will_open_at - now();
    }
    activate_timeout(time) {
        setTimeout(this.after_close_func, time, this);
    }
    after_close_func(that) {
        if (that.next_flyout_to_open !== null) {
            that.next_flyout_to_open.addClass('flyout-active');
            that.next_flyout_to_open = null;
            that.is_any_open = true;
            that.will_open_at = now() + that.open_time;
        }
    }
    close_all() {
        if (this.is_opening_now()) {
            this.all_flyouts.close();
            this.next_flyout_to_open = null;
            this.is_any_open = false;
            this.will_close_at = this.open_time - this.time_until_open();
        } else if (this.is_closing_now()) {
            // pass
        } else if (this.is_any_open) {
            this.all_flyouts.close();
            this.next_flyout_to_open = null;
            this.is_any_open = false;
            this.will_close_at = now() + this.open_time;
            this.activate_timeout(this.open_time)
        } else {
            // pass
        }
    };
    open_flyout(flyout) {
        if (this.is_opening_now()) {
            this.all_flyouts.close();
            this.next_flyout_to_open = flyout;
            this.is_any_open = true;
            this.activate_timeout(this.open_time - this.time_until_open());
        } else if (this.is_closing_now()) {
            this.next_flyout_to_open = flyout;
        } else if (this.is_any_open) {
            this.close_all();
            this.next_flyout_to_open = flyout;
        } else {
            flyout.addClass('flyout-active');
            this.next_flyout_to_open = null;
            this.is_any_open = true;
            this.will_open_at = now() + this.open_time;
        }
    }
}();


$('.collapsible').collapsible();
$('.sidenav > li.with-flyout > a').click(function(elem){
    let flyout = $(this).parent();
    if (flyout.hasClass('flyout-active')) {
        sidenav_flyout.close_all();
    } else {
        sidenav_flyout.open_flyout(flyout);
    }
});

