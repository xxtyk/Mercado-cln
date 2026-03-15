import { Router } from "express";

const MAKE_WEBHOOK = "https://hook.us2.make.com/6i4bkyis6v89kcv5y8if0jp6f545xn1y";

const router = Router();

router.post("/webhook-pedido", async (req, res) => {
  try {
    const response = await fetch(MAKE_WEBHOOK, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body),
    });
    res.status(200).json({ ok: true, status: response.status });
  } catch (err) {
    res.status(500).json({ ok: false, error: String(err) });
  }
});

export default router;
