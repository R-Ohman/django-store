from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from comments.forms import CommentForm, UserReportForm
from comments.models import ProductComment, Attachment, Like
from payments.models import ExchangeRate
from products.models import Product
from products.utils import round_number
from users.translator import translate_text_to_user_language
from users.utils import user_received_product


def product_view(request, product_id):
    if request.method == 'POST':
        form = CommentForm(request.POST, request=request)
        files = request.FILES.getlist('files')

        if form.is_valid():
            user = request.user
            assessment = form.cleaned_data['assessment']
            text = form.cleaned_data['text']
            comment = ProductComment.objects.create(
                user=user,
                assessment=assessment,
                text=text,
                product=Product.objects.get(id=product_id)
            )  # create will create as well as save too in db.
            for file in files:
                Attachment.objects.create(
                    comment=comment,
                    file=file
                )
            message = translate_text_to_user_language('Comment added successfully!', request)
            success = True
        else:
            message = translate_text_to_user_language('Comment not added!', request)
            success = False

        response = product_comments(request, product_id)
        return JsonResponse({
            'success': success,
            'message': message,
            'comments_html': response['comments_html'],
        })
    else:
        form = CommentForm(request=request)

    product = Product.objects.get(id=product_id)
    prev_page = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else '/'
    currency, converted_price = ExchangeRate.get_user_currency_and_converted_product_price(request, product)
    max_user_comments_per_product = 5
    comments = ProductComment.objects.filter(product=product).order_by('-created_at')

    # Pagination
    per_page = int(request.COOKIES.get('per_page', 3))
    page_number = request.GET.get('page', 1)
    paginator = Paginator(comments, per_page)

    try:
        comments_page = paginator.page(page_number)
    except EmptyPage:
        # Return an empty page if the page number is out of range
        comments_page = paginator.page(1)

    # AJAX response
    if request.is_ajax() and request.method == 'GET':
        context = {
            'comments': comments_page,
            'request': request,
        }
        comments_list_html = render_to_string('comments/comments_cards.html', context)
        page_list_html = render_to_string('comments/pagination.html', context)
        return JsonResponse({
            'comments_list_html': comments_list_html,
            'page_list_html': page_list_html
        })

    context = {
        'product': product,
        'previous_page': prev_page,
        'currency': currency,
        'converted_price': round_number(converted_price),
        'discounted_price': round_number(product.discount_multiply(converted_price)),
        'form': form,
        'comments': comments_page,
        'can_comment': user_received_product(request, product) and \
                       ProductComment.objects.filter(user=request.user,
                                                     product=product).count() < max_user_comments_per_product
    }
    return render(request, 'products/product-view.html', context)


@login_required
def like_comment(request, comment_id, is_positive):
    is_positive = 1 if is_positive == 'true' else -1
    comment = ProductComment.objects.get(id=comment_id)
    user_like = Like.objects.filter(user=request.user, comment=comment).first()

    # User has already liked (or disliked) this comment
    if user_like:
        # User has clicked button a second time - remove like/dislike
        if user_like.is_positive_value == is_positive:
            comment.rating -= user_like.is_positive_value
            user_like.delete()
        # User has clicked another button - change like to dislike or vice versa
        else:
            user_like.is_positive_value = is_positive
            comment.rating += 2 * user_like.is_positive_value
            user_like.save()
    else:
        # User has clicked like or dislike for the first time
        user_like = Like.objects.create(
            user=request.user,
            comment=comment,
            is_positive_value=is_positive
        )
        comment.rating += user_like.is_positive_value
    comment.save()
    return JsonResponse({'success': True, 'rating': comment.rating})


# @login_required
# def delete_comment(request, comment_id):
#     try:
#         comment = ProductComment.objects.get(id=comment_id)
#         if comment.user == request.user or request.user.is_staff:
#             comment.delete()
#             messages.success(request, translate_text_to_user_language("Comment deleted successfully!", request))
#         else:
#             messages.error(request, translate_text_to_user_language("You can't delete this comment!", request))
#     except ProductComment.DoesNotExist:
#         messages.error(request, translate_text_to_user_language("Comment does not exist!", request))
#     return redirect(request.META.get('HTTP_REFERER', '/'))


def translate_comment(request, comment_id):
    try:
        comment = ProductComment.objects.get(id=comment_id)
        translated_text = translate_text_to_user_language(comment.text, request)

        return JsonResponse({
            'success': True,
            'translated_text': translated_text,
            'original_text': comment.text,
            'message_translate': translate_text_to_user_language("Show translation", request),
            'message_original': translate_text_to_user_language("Show original", request)
        })
    except ProductComment.DoesNotExist:
        messages.error(request, translate_text_to_user_language("Comment does not exist!", request))
    return JsonResponse({'success': False})


def contact(request):
    if request.method == 'POST':
        form = UserReportForm(request.POST)
        if form.is_valid():
            user_report = form.save(commit=False)
            user_report.user = request.user if request.user.is_authenticated else None
            user_report.save()
            messages.success(request, translate_text_to_user_language("Your message has been sent!", request))
            return redirect('contact')
    else:
        if request.user.is_authenticated:
            initial_data = {
                'name': f'{request.user.first_name} {request.user.last_name}',
                'email': request.user.email,
            }
            form = UserReportForm(initial=initial_data)
        else:
            form = UserReportForm()

    context = {
        'form': form
    }

    return render(request, 'comments/contact.html', context)


def image_view(request, product_id):
    product = Product.objects.get(id=product_id)
    image = product.image
    image_html = f'<img src="{image.url}"/>'
    return HttpResponse(image_html)


def product_comments(request, product_id):
    product = Product.objects.get(id=product_id)
    page = request.GET.get('page', 1)
    print(page)
    print(request.GET.get('page'))
    product_comments = product.comments.all().order_by('-created_at')

    per_page = int(request.COOKIES.get('per_page', 3))
    paginator = Paginator(product_comments, per_page)

    try:
        comments_page = paginator.page(page)
    except EmptyPage:
        comments_page = paginator.page(1)

    context = {
        'comments': comments_page,
        'page': page,
        'request': request,
        'can_comment': user_received_product(request, product) and \
                       ProductComment.objects.filter(user=request.user,
                                                     product=product).count() < 5,
        'form': CommentForm(request=request),
        'product': product,
    }
    comments_html = render_to_string('comments/comments.html', context, request=request)

    return {
        'success': True,
        'message': translate_text_to_user_language("Comment deleted successfully!", request),
        'comments_html': comments_html,
    }

def delete_comment(request, comment_id):
    comment = ProductComment.objects.filter(id=comment_id).first()
    if not comment:
        return JsonResponse({
            'success': False,
            'message': translate_text_to_user_language("Comment does not exist!", request)
        })

    product = comment.product
    comment.delete()
    return JsonResponse(product_comments(request, product.id))
