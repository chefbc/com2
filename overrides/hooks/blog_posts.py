"""
Hook to make blog posts available in template context.
"""
try:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.nav import Navigation
    from mkdocs.structure.pages import Page
except ImportError:
    # Fallback if imports fail
    pass

# Global storage for blog posts collected from navigation
_collected_blog_posts = []


def on_nav(nav, config, files):
    """
    Collect blog posts when navigation is built.
    This runs before on_page_context and gives us access to all pages.
    """
    global _collected_blog_posts
    _collected_blog_posts = []
    
    try:
        from mkdocs.structure.pages import Page as PageClass
        
        def collect_pages(item):
            """Recursively collect all pages from navigation."""
            # Check if it's a Page object
            if isinstance(item, PageClass):
                # Check if it's a blog post (has date and is in blog directory)
                if hasattr(item, 'meta') and item.meta:
                    has_date = item.meta.get('date')
                    is_draft = item.meta.get('draft', False)
                    # Check if URL contains blog/ (but not blog/index)
                    # Blog posts typically have URLs like blog/posts/post-name/ or blog/post-name/
                    # Be more permissive - any URL with blog/ that has a date is likely a post
                    is_blog_url = (
                        item.url and 
                        'blog/' in item.url and 
                        item.url != 'blog/index.html' and 
                        not item.url.endswith('/index.html') and
                        'blog/index' not in item.url and
                        'blog/category' not in item.url and
                        'blog/archive' not in item.url and
                        'blog/author' not in item.url
                    )
                    
                    if has_date and not is_draft and is_blog_url:
                        _collected_blog_posts.append(item)
            
            # Check if it has children (Section objects)
            if hasattr(item, 'children') and item.children:
                for child in item.children:
                    collect_pages(child)
        
        # Collect pages from navigation
        if nav:
            for item in nav:
                collect_pages(item)
        
        # Also check files directly (blog posts might not be in nav)
        if files:
            try:
                for file in files:
                    # Check if file is a blog post by source path
                    if hasattr(file, 'src_path'):
                        src_path = file.src_path
                        # Blog posts are typically in blog/posts/ directory
                        is_blog_post_file = (
                            'blog/posts' in src_path or 
                            (src_path.startswith('blog/') and src_path.endswith('.md') and 'index' not in src_path)
                        )
                        
                        if is_blog_post_file:
                            # Try to get the page associated with this file
                            page_obj = None
                            if hasattr(file, 'page') and file.page:
                                page_obj = file.page
                            elif hasattr(file, 'url'):
                                # Try to find the page by URL in nav
                                for item in nav or []:
                                    if hasattr(item, 'url') and item.url == file.url:
                                        if isinstance(item, PageClass):
                                            page_obj = item
                                        break
                            
                            if page_obj and hasattr(page_obj, 'meta') and page_obj.meta:
                                has_date = page_obj.meta.get('date')
                                is_draft = page_obj.meta.get('draft', False)
                                if has_date and not is_draft:
                                    # Check if we already have this post
                                    if page_obj not in _collected_blog_posts:
                                        _collected_blog_posts.append(page_obj)
            except Exception as e:
                # Silently continue if file access fails
                pass
        
        # Sort blog posts by date
        def get_sort_date(post):
            """Get sortable date from post."""
            if hasattr(post, 'meta') and post.meta:
                date = post.meta.get('date')
                if date:
                    if isinstance(date, str):
                        # Extract date part from string (handle ISO format)
                        date_str = date.split('T')[0]
                        return date_str
                    else:
                        # For date objects, convert to string
                        return str(date)
            return '0000-00-00'
        
        _collected_blog_posts.sort(key=get_sort_date, reverse=True)
        
        # Limit to 11 posts (1 featured + 10 smaller)
        _collected_blog_posts = _collected_blog_posts[:11]
        
    except Exception:
        _collected_blog_posts = []
    
    return nav


def on_page_context(context, page, config, nav):
    """
    Add all pages to the page context so they're available in templates.
    Also identify blog posts specifically.
    Tries to access blog plugin's internal data first, then falls back to navigation-based collection.
    """
    try:
        from mkdocs.structure.pages import Page as PageClass
        
        # Collect all pages from navigation recursively
        all_pages = []
        blog_posts = []
        seen_urls = set()
        
        # Try to get all pages from files if available (more reliable)
        try:
            if hasattr(config, 'plugins') and 'blog' in str(config.plugins):
                # Try to access files through the page's file structure
                # This requires accessing the files collection
                pass
        except Exception:
            pass
        
        # Try to access blog plugin's internal data structures first
        blog_plugin = None
        try:
            # Access plugins from config
            if hasattr(config, 'plugins'):
                # plugins can be a dict, PluginCollection, or list depending on MkDocs version
                plugins_to_check = []
                
                if isinstance(config.plugins, dict):
                    plugins_to_check = config.plugins.items()
                elif hasattr(config.plugins, '__iter__'):
                    # Handle PluginCollection or list
                    try:
                        # Try to iterate as dict-like
                        plugins_to_check = config.plugins.items() if hasattr(config.plugins, 'items') else []
                    except (AttributeError, TypeError):
                        # Fall back to list iteration
                        plugins_to_check = [(None, p) for p in config.plugins if hasattr(p, '__class__')]
                
                # Search for blog plugin
                for plugin_name, plugin_instance in plugins_to_check:
                    # Check if this is the blog plugin by name or class
                    is_blog_plugin = (
                        plugin_name == 'blog' or 
                        (hasattr(plugin_instance, '__class__') and 'blog' in plugin_instance.__class__.__name__.lower()) or
                        (hasattr(plugin_instance, 'config') and isinstance(plugin_instance.config, dict) and plugin_instance.config.get('enabled', True))
                    )
                    
                    if is_blog_plugin:
                        # Try to access posts from plugin
                        if hasattr(plugin_instance, 'posts'):
                            blog_plugin = plugin_instance
                            break
                        elif hasattr(plugin_instance, 'blog_posts'):
                            blog_plugin = plugin_instance
                            break
        except Exception:
            # If plugin access fails, continue with fallback method
            pass
        
        # If we found the blog plugin, try to get posts from it
        if blog_plugin:
            try:
                if hasattr(blog_plugin, 'posts'):
                    plugin_posts = blog_plugin.posts
                    if plugin_posts:
                        # Convert plugin posts to our format
                        for post in plugin_posts:
                            # Filter out drafts and ensure it has required attributes
                            if hasattr(post, 'meta') and post.meta:
                                is_draft = post.meta.get('draft', False)
                                has_date = post.meta.get('date')
                                if has_date and not is_draft:
                                    blog_posts.append(post)
                elif hasattr(blog_plugin, 'blog_posts'):
                    plugin_posts = blog_plugin.blog_posts
                    if plugin_posts:
                        for post in plugin_posts:
                            if hasattr(post, 'meta') and post.meta:
                                is_draft = post.meta.get('draft', False)
                                has_date = post.meta.get('date')
                                if has_date and not is_draft:
                                    blog_posts.append(post)
            except Exception:
                # If accessing plugin data fails, fall back to navigation method
                pass
        
        # Fallback: Collect pages from navigation if we didn't get posts from plugin
        if not blog_posts:
            def collect_pages(item):
                """Recursively collect all pages from navigation."""
                # Check if it's a Page object
                if isinstance(item, PageClass):
                    if item.url and item.url not in seen_urls:
                        all_pages.append(item)
                        seen_urls.add(item.url)
                        
                        # Check if it's a blog post (has date and is in blog directory)
                        if hasattr(item, 'meta') and item.meta:
                            has_date = item.meta.get('date')
                            is_draft = item.meta.get('draft', False)
                            # Check if URL contains blog/ (but not blog/index)
                            # Also check for blog post URLs like blog/posts/... or just blog/...
                            is_blog_url = (
                                item.url and 
                                ('blog/' in item.url or item.url.startswith('blog/')) and 
                                item.url != 'blog/index.html' and 
                                not item.url.endswith('/index.html') and
                                'blog/index' not in item.url
                            )
                            
                            if has_date and not is_draft and is_blog_url:
                                blog_posts.append(item)
                
                # Check if it has children (Section objects)
                if hasattr(item, 'children') and item.children:
                    for child in item.children:
                        collect_pages(child)
                
                # Check if it has a url attribute and meta (might be a page-like object)
                if hasattr(item, 'url') and item.url and hasattr(item, 'meta'):
                    if item.url not in seen_urls:
                        all_pages.append(item)
                        seen_urls.add(item.url)
                        
                        # Check if it's a blog post
                        if item.meta:
                            has_date = item.meta.get('date')
                            is_draft = item.meta.get('draft', False)
                            is_blog_url = (
                                item.url and 
                                ('blog/' in item.url or item.url.startswith('blog/')) and 
                                item.url != 'blog/index.html' and 
                                not item.url.endswith('/index.html') and
                                'blog/index' not in item.url
                            )
                            
                            if has_date and not is_draft and is_blog_url:
                                blog_posts.append(item)
            
            # Collect pages from navigation
            if nav:
                for item in nav:
                    collect_pages(item)
            
            # Also try to get all pages from the files structure if available
            # This is a more reliable way to get blog posts
            try:
                if hasattr(page, 'file') and hasattr(page.file, 'src_path'):
                    # We're on a specific page, but we need all pages
                    # Try to get from config or environment
                    pass
            except Exception:
                pass
        
        # Sort blog posts by date
        def get_sort_date(post):
            """Get sortable date from post."""
            if hasattr(post, 'meta') and post.meta:
                date = post.meta.get('date')
                if date:
                    if isinstance(date, str):
                        # Extract date part from string (handle ISO format)
                        date_str = date.split('T')[0]
                        return date_str
                    else:
                        # For date objects, convert to string
                        return str(date)
            return '0000-00-00'
        
        # If we still don't have blog posts, use the ones collected in on_nav
        if not blog_posts:
            blog_posts = _collected_blog_posts
        
        # Sort blog posts by date (in case we got new ones)
        blog_posts.sort(key=get_sort_date, reverse=True)
        
        # Limit to 11 posts (1 featured + 10 smaller)
        blog_posts = blog_posts[:11]
        
        # Calculate readtime for posts that don't have it
        for post in blog_posts:
            if hasattr(post, 'meta') and post.meta:
                if not post.meta.get('readtime'):
                    # Try to calculate readtime from content
                    content_text = ''
                    try:
                        # Try to get content from various sources
                        if hasattr(post, 'content') and post.content:
                            import re
                            # Strip HTML tags
                            content_text = re.sub(r'<[^>]+>', '', post.content)
                        elif hasattr(post, 'markdown') and post.markdown:
                            content_text = post.markdown
                        elif hasattr(post, 'file') and hasattr(post.file, 'src_path'):
                            # Try to read from source file
                            import os
                            from mkdocs.config.defaults import MkDocsConfig
                            if hasattr(config, 'docs_dir'):
                                file_path = os.path.join(config.docs_dir, post.file.src_path)
                                if os.path.exists(file_path):
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        # Remove front matter
                                        if content.startswith('---'):
                                            parts = content.split('---', 2)
                                            if len(parts) >= 3:
                                                content = parts[2]
                                        # Strip markdown syntax roughly
                                        import re
                                        content_text = re.sub(r'[#*\[\](){}`]', '', content)
                    except Exception:
                        pass
                    
                    if content_text:
                        # Calculate words (rough estimate)
                        words = len(content_text.split())
                        # Average reading speed: 265 words per minute
                        words_per_minute = 265
                        readtime = max(1, int(round(words / words_per_minute)))
                        post.meta['readtime'] = readtime
        
        # Make pages available in template context
        context['all_pages'] = all_pages
        context['pages'] = all_pages  # Also add as 'pages' for compatibility
        context['blog_posts'] = blog_posts  # Add blog posts specifically
        
    except Exception as e:
        # If anything fails, just ensure the variables exist
        context['all_pages'] = []
        context['pages'] = []
        context['blog_posts'] = []
    
    return context
