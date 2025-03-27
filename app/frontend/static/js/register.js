$(document).ready(function() {
    var form = $(".tab-wizard2").steps({
        headerTag: "h5",
        bodyTag: "section",
        transitionEffect: "fade",
        titleTemplate: '<span class="step">#index#</span> #title#',
        labels: {
            finish: "Submit",
            next: "Next",
            previous: "Previous",
        },
        onStepChanging: function(event, currentIndex, newIndex) {
            // Validate form before moving to next step
            if (currentIndex < newIndex) {
                return validateStep(currentIndex);
            }
            return true;
        },
        onFinishing: function(event, currentIndex) {
            return validateStep(currentIndex) && submitForm();
        },
        onFinished: function(event, currentIndex) {
            // Handled in onFinishing
        }
    });

    function validateStep(stepIndex) {
        let isValid = true;
        let requiredFields;

        switch(stepIndex) {
            case 0: // Personal Information
                requiredFields = ['full_name', 'gender'];
                break;
            case 1: // Account Credentials
                requiredFields = ['email', 'username', 'password', 'confirm_password'];
                break;
            case 2: // Overview
                requiredFields = ['terms'];
                break;
        }

        requiredFields.forEach(field => {
            let $input = $(`[name="${field}"]`);
            if ($input.attr('type') === 'checkbox') {
                if (!$input.is(':checked')) {
                    isValid = false;
                    $input.addClass('is-invalid');
                } else {
                    $input.removeClass('is-invalid');
                }
            } else if (!$input.val() || ($input.attr('type') === 'radio' && !$input.is(':checked'))) {
                isValid = false;
                $input.addClass('is-invalid');
            } else {
                $input.removeClass('is-invalid');
            }
        });

        // Special validation for password confirmation
        if (stepIndex === 1) {
            let password = $('[name="password"]').val();
            let confirm = $('[name="confirm_password"]').val();
            if (password !== confirm) {
                isValid = false;
                $('[name="confirm_password"]').addClass('is-invalid');
            }
        }

        return isValid;
    }

    function submitForm() {
        const formData = {
            personal_info: {
                full_name: $('[name="full_name"]').val(),
                gender: $('[name="gender"]:checked').val(),
                city: $('[name="city"]').val(),
                state: $('[name="state"]').val()
            },
            credentials: {
                email: $('[name="email"]').val(),
                username: $('[name="username"]').val(),
                password: $('[name="password"]').val()
            },
            terms_accepted: $('[name="terms"]').is(':checked')
        };

        $.ajax({
            url: '/api/register',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                $('#success-modal-btn').click();
            },
            error: function(xhr) {
                let errorMsg = xhr.responseJSON?.detail || 'Registration failed';
                alert(errorMsg);
            }
        });

        // Prevent default finish behavior
        return false;
    }

    // Update overview section when reaching last step
    form.on('stepChanged', function(event, currentIndex) {
        if (currentIndex === 2) {
            $('.register-info li').each(function(index) {
                let $value = $(this).find('.col-sm-8');
                switch(index) {
                    case 0: $value.text($('[name="email"]').val()); break;
                    case 1: $value.text($('[name="username"]').val()); break;
                    case 2: $value.text('••••••••'); break;
                    case 3: $value.text($('[name="full_name"]').val()); break;
                    case 4: $value.text(`${$('[name="city"]').val()} ${$('[name="state"]').val()}`.trim()); break;
                }
            });
        }
    });
});