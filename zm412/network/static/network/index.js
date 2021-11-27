
let user_id = document.querySelector('#user_info').dataset.userid;
let counter = 1;
const limit_num = 5;
let quantity ;
let listing_on = true;


document.addEventListener('DOMContentLoaded', function() {
  quantity = localStorage.getItem('quantity') || document.querySelector('#user_info').dataset.quantity;

  document.querySelector('#followings_posts').onclick = get_followings_posts;
  document.querySelector('#user_info').onclick = (e) =>  show_user_func(user_id) 
  document.querySelector('#all_posts').addEventListener('click', () =>  load_page('all_posts'));
  document.querySelector('#add_new_link').addEventListener('click', () => {
    load_page('add_new');
    document.querySelector('#form_add').onsubmit = (e) => save_post(e);
  });
  load_page('all_posts')
})

function create_listing_page(arr_posts, user_id, page_destination){
  listing_on = true;
  document.querySelector('#list_of_posts').innerHTML = '';
  let pagination_block = document.querySelector('#pagination_block');
  let button_next = document.querySelector('#button_next');
  let button_prev = document.querySelector('#button_prev');
  button_next.dataset.destination = page_destination;
  button_prev.dataset.destination = page_destination;
  let page_num = document.querySelector('#page_num');
  button_next.onclick = butt_next;
  button_prev.onclick = butt_prev;

  let last_page = Math.ceil( quantity / limit_num );
  if(quantity > limit_num){
    pagination_block.style.display = 'block';
    page_num.style.display = 'inline';
    page_num.innerHTML = `${counter} page of ${last_page}`;
    button_prev.style.display = counter == 1 ? 'none' : counter == last_page ? 'inline' : 'inline';
    button_next.style.display = counter == 1 ? 'inline' : counter == last_page ? 'none' : 'inline';
  }else{
    pagination_block.style.display = 'none';
  } 
  arr_posts.forEach(item => each_post_html(item, user_id));
}

function butt_prev(e){
  --counter;
  let start = ( counter - 1 ) * limit_num;
  let end = ( counter  ) * limit_num;
  let post_owner_id = localStorage.getItem('post_owner_id')
  get_posts(start, end, post_owner_id, e.target.dataset.destination);
}

function butt_next(e){
  let start = counter * limit_num;
  let end = ( counter + 1 ) * limit_num;
  let post_owner_id = localStorage.getItem('post_owner_id')
  get_posts(start, end, post_owner_id, e.target.dataset.destination);
  ++counter;
}

function load_page(page_name, post_owner_id=0){
  let elem = change_class(page_name);
  if(page_name == 'all_posts' || page_name == 'followings_posts_list'){
      get_posts(0, limit_num, post_owner_id, page_name);
  }
  return elem;
}

function change_class(page_name){
  let selector = '#'+page_name;
  let list = ['#all_posts', '#followings_posts_list', '#add_new', '#profile', '#users_list'];
  let blockElem = document.querySelector(selector);
  let head_title = document.querySelector('#title_page');
  list.forEach(item => {
    if(item == selector){
      classElem = 'block';
    }else{
      classElem = 'none';
    }
    document.querySelector('#listing').style.display = listing_on || item == 'add_new' ? 'none' : 'block' ;
    document.querySelector(item).style.display = classElem;
    if(item == 'add_new') localStorage.setItem('page_destination', 'add_new');
  })
  return blockElem;
}

function get_followings_posts(){
  counter = 1;
  listing_on = true;
  localStorage.setItem('page_destination', 'followings_posts_list');
  load_page('followings_posts_list', -1);
}

window.onpopstate = function (e){
  
  if(e.state){
    let page = e.state.page_destination;
    change_class(page);
    if(page == 'profile'){
        show_user_func(e.state.following_user_id)
        counter = Math.floor( e.state.end / limit_num );
      }else if(page == 'users_list'){
        get_list_users_html(e.state.arr);
      }else if(page == 'all_posts' || page == 'followings_posts_list'){
        get_posts(e.state.start, e.state.end, e.state.post_owner_id, page);
        counter = Math.floor( e.state.end / limit_num );
      }
  }
  
}

function show_user_func(following_user_id){
  localStorage.setItem('following_user_id', following_user_id);
  counter = 1;
  listing_on = true;
  let par = load_page('profile', following_user_id);
  document.querySelector("#listing").style.display = 'block';
  get_profile_info(following_user_id);
}

function get_profile_info(following_user_id){
  console.log(following_user_id, 'followUser')
  let user_name = document.querySelector('#username_info');
  let a_followers = document.querySelector('#followers_list');
  let a_following = document.querySelector('#followings_list');
  get_posts(0, limit_num, following_user_id, 'profile')
    .then(async obj => {
      let name_of_butt;
      await fetch(`user_info/${following_user_id}`)
        .then(response => response.json())
        .then(result => {
          console.log(user_id, following_user_id, 'usersid')
          if(user_id != following_user_id){
            let follow_butt = document.querySelector('#follow_butt');
            follow_butt.style.display = 'block';
            follow_butt.innerHTML = result.is_following ? 'Unfollow': 'Follow'

            follow_butt.onclick = (e) => {
              let inner = e.target.innerHTML.toLowerCase();
              follow_btn(obj, inner, following_user_id);
            }
          }else{
            follow_butt.style.display = 'none';
          }
        })
        .catch(error => console.log(error, 'error'))

        user_name.innerHTML = obj.author;
        a_followers.innerHTML = obj.followers.length;
        a_following.innerHTML = obj.following.length;
        a_followers.onclick = (e) => get_list_users_html(obj.followers);
        a_following.onclick = (e) => get_list_users_html(obj.following);
      })
      .catch(err => console.log(err, 'error'))

}

function follow_btn(obj, inner, user_id){
  fetch(`follow/${obj.following_user}/${inner}`)
    .then(response => response.json())
    .then(res => {
      console.log(res, 'res')
      get_profile_info(user_id);
    })
    .catch(err => console.log(err, 'err1'))

}

async function get_posts(start, end, post_owner_id=0, page_destination){
  let obj_history = {start, end, post_owner_id, page_destination};
  if(page_destination == 'profile'){
    obj_history.following_user_id = localStorage.getItem('following_user_id')
  } 

  history.pushState(obj_history, '', '');
  let span_user = document.querySelector('#user_span');
  localStorage.setItem('start', start);
  localStorage.setItem('end', end);
  localStorage.setItem('post_owner_id', post_owner_id);
  localStorage.setItem('page_destination', page_destination);

  document.querySelector("#listing").style.display = 'block';
  let obj;
  
  await fetch( `posts/?post_owner_id=${post_owner_id}&start=${start}&end=${end}`)
    .then(response => response.json())
    .then(result => {
        localStorage.setItem('quantity', result.quantity);
        quantity = result.quantity;
        create_listing_page(result.posts, user_id, page_destination);
        obj = result;
        span_user.innerHTML = post_owner_id == 0 ? 'all users' : post_owner_id < 0 ? 'following users' : `user ${result.author}`;
      })
    .catch(err => console.log(err, 'error'))

  return obj;
}

function each_post_html(obj, user_id){
  let if_likes = obj.likers.some(item => item.id == user_id);
  let list_of_posts = document.querySelector('#list_of_posts');
  let new_line = createEl('div', list_of_posts, { 'class':"p-4 mb-3 border show_elem new_line" }) ;
  let author = createEl('a', new_line, {'href': '#', 'class': 'author_style'}, obj.author_name) ;
  let edit_link = createEl('p', new_line, {'class': ''}, '');
  let created = createEl('div', new_line, {'class': 'date_style'}, 'Created: '+obj.created) ;
  let updated = createEl('div', new_line, {'class': 'data_style'}, 'Updated: '+obj.updated) ;

  let title = createEl('p', new_line, {'class': 'title_style'}, 'Title: ' +obj.title) ;
  let post_body = read_next(obj.body, 50, new_line) ;
  let new_like = createEl('a', new_line, {'href': '#', 'class': 'new_like_style'}) ;
  let likes_num = createEl('a', new_line, {'href': '#'}, `${obj.likers.length} likes`) ;
  let img_src = if_likes ?  "https://img.icons8.com/fluent/22/000000/filled-like.png" :
            "https://img.icons8.com/material-outlined/20/000000/filled-like.png"
  let img = createEl('img', new_like, {'src': img_src}) ;

  new_like.onclick = (e) => add_like(obj.id);
  author.onclick = (e) => show_user_func(obj.author_id);
  edit_post(edit_link, post_body, obj);

  likes_num.onclick = (e) => {
    e.preventDefault();
    listing_on = false;
    list_of_posts.innerHTML = '';
    get_list_users_html(obj.likers)
  }
}

function read_next(str, num, par){
  let elem = createEl('p', par, {'class': 'text_style'}, '');
  if(str.length > num){
    let first_part = str.slice(0, num);
    let second_part = str.slice(num, str.length-1);
    let first = createEl('span', elem, {}, first_part);
    let second = createEl('span', elem, {'class': 'hide_elem read_more_style'}, second_part);
    let a = createEl('a', elem, {'href': '#', 'class': 'read_more_style '}, ' ...read full post');
    a.onclick = (e) => {
        second.classList.toggle('hide_elem');
        a.innerHTML = second.classList.contains('hide_elem') ? '...read full text' : 'hide';
    }
  } else{
    let body = createEl('span', elem, {}, str);
  }
    return elem;
}

function edit_post(par, post_body, obj){
  if(user_id == obj.author_id){
    let edit_link = createEl('a', par, { 'href': '#', 'style': 'display: block ;' }, 'Edit') ;
    edit_link.addEventListener('click', async function(e){
      post_body.innerHTML = '';
      edit_link.style.display = 'none';

      post_body.insertAdjacentHTML('afterbegin', `
          <form method='POST' id='form_upd' data-postid=${obj.id} >
            <textarea name="body" cols="30" rows="10">${obj.body}</textarea>
            <button class='col-sm-2 btn btn-outline-secondary'>Save</button>
          </form>
            <button class='col-sm-2 btn btn-outline-secondary'  onclick="reload_page()">Cancel</button>
      `);
      
      formElem = document.querySelector('#form_upd');
      formElem.onsubmit = (e) => save_post(e); 
    })
  }
}

async function save_post(e){
  e.preventDefault();
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  response = await fetch(`save_post/${e.target.dataset.postid}`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrftoken },
      body: new FormData(e.target) 
  });
  let result = await response.json();
  show_result_of_save_post(result, message);
  e.target.reset();
}

function show_result_of_save_post(obj, elem){
  elem.style.color = obj.status ? 'blue' : 'red';
  obj.message == 'Successfully added' ? load_page('all_posts') : reload_page();
  document.querySelector('#add_new').style.display = 'none';
  setTimeout(() => elem.innerHTML = '' , 5000); 
  elem.innerHTML = obj.message;
}

function add_like(post_id){
  fetch('posts/'+post_id)
    .then(response => response.json())
    .then(result =>reload_page())
    .catch(err => console.log(err, 'error'))
}

function reload_page(){
  let start = localStorage.getItem('start');
  let end = localStorage.getItem('end');
  let post_owner_id = localStorage.getItem('post_owner_id')
  let page_destination = localStorage.getItem('page_destination')
  get_posts(start, end, post_owner_id, page_destination);
}

function get_list_users_html(arr = []){
  let list_elem = load_page('users_list');
  document.querySelector("#listing").style.display = 'none';
  listing_on = false;
  list_elem.innerHTML = '';
  let ul = createEl('ul', list_elem, {}, '') ;

  for(let elem of arr){
    let li = createEl('li', ul, {}, '') ;
    let a = createEl('a', li, {"href": '#'}, elem.username) ;
    a.onclick = (e) => show_user_func(elem.id);
  }
  localStorage.setItem('page_destination', 'users_list');
  history.pushState({ arr, page_destination: 'users_list' }, '', '');
  return list_elem; 
}

function createEl(tag, par, objAttr={}, inner=''){
  new_el = document.createElement(tag);
  for(key in objAttr){
    new_el.setAttribute(key, objAttr[key]);
  }
  new_el.innerHTML = inner;
  par.append(new_el);
  return new_el;
}


