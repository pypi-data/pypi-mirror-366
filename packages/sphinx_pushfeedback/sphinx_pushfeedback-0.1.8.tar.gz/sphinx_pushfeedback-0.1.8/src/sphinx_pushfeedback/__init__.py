"""
Feedback widget for Sphinx.

(c) 2023 - present PushFeedback.com
This code is licensed under MIT license (see LICENSE.md for details).
"""

__version__ = "0.1.8"

from sphinx.application import Sphinx


class FeedbackExtension:
    DEFAULT_OPTIONS = {
        # button props
        'session_id': None,
        'button_position': 'bottom-right',
        'button_style': "dark",
        'feedback_button_text': 'Send feedback',
        'hide_icon': None,
        'hide_mobile': None,
        'metadata': None,
        # modal props
        'custom_font': None,
        'email_address': None,
        'hide_email': None,
        'hide_privacy_policy': None,
        'hide_rating': None,
        'hide_screenshot_button': None,
        'modal_position': "bottom-right",
        'project': None,
        'rating': None,
        'rating_mode': None,
        'email_placeholder': None,
        'error_message': None,
        'error_message_4_0_3': None,
        'error_message_4_0_4': None,
        'footer_text': None,
        'message_placeholder': None,
        'modal_title': None,
        'modal_title_error': None,
        'modal_title_success': None,
        'privacy_policy_text': None,
        'rating_placeholder': None,
        'rating_stars_placeholder': None,
        'send_button_text': None,
        # screenshot text props
        'screenshot_attached_text': None,
        'screenshot_button_text': None,
        'screenshot_taking_text': None,
        'screenshot_edit_text_button_text': None,
        'screenshot_editor_title': None,
        'screenshot_editor_cancel_text': None,
        'screenshot_editor_save_text': None,
        'screenshot_size_label_text': None,
        'screenshot_border_label_text': None,
        'screenshot_edit_text_prompt_text': None,
        'screenshot_error_general': None,
        'screenshot_error_permission': None,
        'screenshot_error_not_supported': None,
        'screenshot_error_not_found': None,
        'screenshot_error_cancelled': None,
        'screenshot_error_browser_not_supported': None,
        'screenshot_error_unexpected': None,
    }

    def __init__(self, app: Sphinx):
        self.app = app
        self.setup_options()
        self.setup_events()

    @staticmethod
    def snake_to_kebab(string):
        """Convert snake_case string to kebab-case."""
        return string.replace('_', '-')

    def inject_feedback_scripts(self, app, pagename, templatename, context, doctree):
        feedback_css_link = '''
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pushfeedback/dist/pushfeedback/pushfeedback.css" type="text/css">
        '''
        
        feedback_js_module = '''
            <script type="module" src="https://cdn.jsdelivr.net/npm/pushfeedback/dist/pushfeedback/pushfeedback.esm.js"></script>
        '''

        # Add feedback CSS and JS module to body
        context.setdefault('body', '')
        context['body'] += feedback_css_link + feedback_js_module

        if getattr(app.config, "pushfeedback_button_position", None) != "default":
            attribute_pairs = [
                f'feedbackBtn.setAttribute("{self.snake_to_kebab(key)}", "{getattr(app.config, f"pushfeedback_{key}")}");'
                for key in self.DEFAULT_OPTIONS.keys() if getattr(app.config, f"pushfeedback_{key}") is not None
            ]
            set_attributes_script = "\n                    ".join(attribute_pairs)
            
            feedback_button_text = getattr(app.config, "pushfeedback_feedback_button_text", self.DEFAULT_OPTIONS['feedback_button_text'])

            feedback_script = f'''
                <script>
                    window.addEventListener('DOMContentLoaded', (event) => {{
                        let feedbackBtn = document.createElement("feedback-button");
                        feedbackBtn.innerHTML = "{feedback_button_text}";
                        {set_attributes_script}
                        document.body.appendChild(feedbackBtn);
                    }});
                </script>
            '''
            context['body'] += feedback_script

    def setup_options(self):
        for key in self.DEFAULT_OPTIONS.keys():
            self.app.add_config_value(f'pushfeedback_{key}', self.DEFAULT_OPTIONS[key], 'html')

    def setup_events(self):
        self.app.connect('html-page-context', self.inject_feedback_scripts)


def setup(app: Sphinx):
    extension = FeedbackExtension(app)
    
    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
