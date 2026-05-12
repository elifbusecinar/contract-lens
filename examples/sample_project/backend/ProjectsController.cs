using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace Sample.Backend;

[ApiController]
[Route("api/projects")]
[Authorize]
public class ProjectsController : ControllerBase
{
    // Drift: frontend posts to `/files` and expects `id` + `thumbnailUrl`.
    // Auth drift sample: UI hints Client-tier upload but this action requires Architect/Admin roles.
    [Authorize(Roles = "Admin,Architect")]
    [HttpPost("{projectId}/models")]
    public IActionResult UploadModel(Guid projectId, IFormFile file)
    {
        return Ok(new
        {
            projectId = projectId,
            thumbnail_path = "/thumbnails/model.png"
        });
    }

    // Drift: frontend reads `name`, backend returns `title`.
    [HttpGet("{projectId}/detail")]
    public IActionResult Detail(Guid projectId)
    {
        return Ok(new { title = "demo", created_at = System.DateTime.UtcNow });
    }
}
